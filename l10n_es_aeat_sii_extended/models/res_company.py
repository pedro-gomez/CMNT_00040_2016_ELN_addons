# -*- coding: utf-8 -*-
# Copyright 2017 El Nogal - Pedro Gómez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    sii_check_invoice_date = fields.Boolean(
        string='Check invoice date',
        default=True,
        help="Check it to verify the invoice date (at invoice validation)\n"
             "Only if method is automatic.\n"
             "Maximum 4 days from invoice date (8 days if date <= 31/12/2017)")
