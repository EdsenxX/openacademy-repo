# -*- coding: utf-8 -*- 

from odoo import models, fields, api, exceptions
from psycopg2 import IntegrityError
from datetime import timedelta

class Course(models.Model):
    _name = 'openacademy.course'
    _description = 'openacademy.course'

    name = fields.Char(string="Title",required=True)
    description = fields.Text()
    responsable_id = fields.Many2one(
            'res.users',
            string="Responsible", 
            index=True,
            ondelete='set null',
            default=lambda self,*a: self.env.uid)
    session_ids = fields.One2many('openacademy.session', 'course_id')

    _sql_constraints = [
        ('name_description_check',
         'CHECK(name != description)',
         "The title of the course should not be the description"
        ),
        (
            'name_unique',
            'UNIQUE(name)',
            "The Course title must be unique"
        )
    ]

    def copy(self, default=None):
        if default is None:
            default = {}
        copied_count = self.search_count([
            ('name', 'ilike', 'Copy of %s%%' % (self.name))
        ])
        if not copied_count:
            new_name = "Copy of %s" % (self.name)
        else:
            new_name = "Copy of %s (%s)" % (self.name, copied_count)
        default['name'] = new_name
        return super(Course, self).copy(default)





class Session(models.Model):
    _name = 'openacademy.session'
    _description = 'openacademy.session'

    name = fields.Char(required=True)
    start_date = fields.Date(default=fields.Date.today)
    duration = fields.Float(digits=(6,2), help="Duration in days")
    seats = fields.Integer(string="Number of seats")
    instructor_id = fields.Many2one('res.partner', string="Instructor", domain=[('instructor', '=', True)])
    course_id = fields.Many2one('openacademy.course', ondelte='cascade', string='Course', required=True)
    attendee_id = fields.Many2many('res.partner',string="Attendees")
    taken_seats = fields.Float(compute="_taken_seats")
    active = fields.Boolean(default=True)
    end_date = fields.Date(store=True,compute='_get_end_date', inverse="_set_end_date")
    attendees_count = fields.Integer(compute='_get_attendees_count', store=True)
    color = fields.Float()
    hours = fields.Float(string="Duration in hours", computed="_get_hours", inverse="_set_hours")

    @api.depends('duration')
    def _get_hours(self):
        for r in self:
            r.hours = r.duration * 24

    def set_hours(self):
        for r in self:
            r.duration = r.hours / 24

    @api.depends('attendee_id')
    def _get_attendees_count(self):
        for record in self.filtered('seats'):
                record.attendees_count = len(record.attendee_id) 

    @api.depends('seats', 'attendee_id')
    def _taken_seats(self):
        for record in self.filtered('seats'):
                record.taken_seats = 100.0 * len(record.attendee_id) / record.seats
   
    @api.depends('start_date', 'duration')
    def _get_end_date(self):
        for record in self.filtered('start_date'):
            start_date = fields.Datetime.from_string(record.start_date)
            record.end_date = start_date + timedelta(days=record.duration,seconds=-1)
    
    @api.depends('start_date', 'duration')
    def _set_end_date(self):
        for record in self.filtered('start_date'):
            start_date = fields.Datetime.from_string(record.start_date)
            end_date = fields.Datetime.from_string(record.end_date)
            record.duration = (end_date - start_date).days + 1


    @api.onchange('seats','attendee_id')
    def _verify_valid_seats(self):
        if self.seats < 0:
            self.active = False
            return {
                    "warning": {
                        "title": "Incorrect 'seats' value",
                        "message": "The number of avaible seats may not be negative",
                        }
                    }
        if self.seats < len(self.attendee_id):
            self.active = False
            return {
                    "warning": {
                        "title": "Too many attendess",
                        "message": "Increase seats or remove excess attendees",
                        }
                    }
        self.active = True

    @api.constrains('instructor_id', 'attendee_id') 
    def _check_instructor_not_in_attendees(self):
       for record in self.filtered('instructor_id'):
           if record.instructor_id in record.attendee_id:
               raise exceptions.ValidationError("A seesion's instructor can't be an attendee")



