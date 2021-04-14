# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Course(models.Model):
    _name = 'openacademy.course'
    _description = 'openacademy.course'

    name = fields.Char(string="Title",required=True)
    description = fields.Text()
    responsable_id = fields.Many2one(
            'res.users',
            string="Responsible", 
            index=True,
            ondelete='set null')
    session_ids = fields.One2many('openacademy.session', 'course_id')


class Session(models.Model):
    _name = 'openacademy.session'
    _description = 'openacademy.session'

    name = fields.Char(required=True)
    start_date = fields.Date()
    duration = fields.Float(digits=(6,2), help="Duration in days")
    seats = fields.Integer(string="Number of seats")
    instructor_id = fields.Many2one('res.partner', string="Instructor")
    course_id = fields.Many2one('openacademy.course', ondelte='cascade', string='Course', required=True)
    attendee_id = fields.Many2many('res.partner',string="Attendees")
