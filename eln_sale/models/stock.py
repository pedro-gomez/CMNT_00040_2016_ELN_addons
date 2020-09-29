# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Marta Vázquez Rodríguez$ <marta@pexego.es>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    supplier_id = fields.Many2one(
        string="Supplier",
        comodel_name='res.partner',
        readonly=True, select=True,
        domain = [('supplier','=',True)],
        states={'draft': [('readonly', False)]})
    carrier_id = fields.Many2one(
        string="Carrier",
        comodel_name='res.partner',
        readonly=True, select=True,
        states={'draft': [('readonly', False)], 'confirmed': [('readonly', False)], 'assigned': [('readonly', False)]})
    requested_date = fields.Date(
        string='Requested Date',
        states={'cancel': [('readonly', True)]},
        help="Date by which the customer has requested the items to be delivered.")
    effective_date = fields.Date(
        string='Effective Date',
        readonly=True,
        states={'done': [('readonly', False)]},
        default=fields.Datetime.now,
        help="Date on which the delivery order was delivered.")
    supplier_cip = fields.Char(
        string='CIP',
        related="sale_id.supplier_cip",
        readonly=True,
        help="Internal supplier code.")
    sent_to_supplier = fields.Boolean(
        string='Sent to Supplier',
        readonly=True,
        states={'done': [('readonly', False)], 'cancel': [('readonly', False)]},
        default=False,
        help="Check this box if the physical delivery note has been sent to the supplier")

    @api.multi
    def write(self, vals):
        res = super(StockPicking, self).write(vals)
        if 'effective_date' in vals:
            orders = self.mapped('sale_id')
            orders.update_effective_date()
        return res


class StockMove(models.Model):
    _inherit = 'stock.move'

    supplier_id = fields.Many2one(
        string="Supplier",
        comodel_name='res.partner',
        related="picking_id.supplier_id",
        readonly=True, store=False, select=True)
    effective_date = fields.Date(
        string='Effective Date',
        related="picking_id.effective_date",
        readonly=True, store=True,
        help="Date on which the delivery order was delivered.")
