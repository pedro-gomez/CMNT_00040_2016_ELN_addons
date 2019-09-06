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
from openerp.osv import orm, fields
from openerp.addons.decimal_precision import decimal_precision as dp


class mrp_indicators_oee(orm.Model):
    _name = 'mrp.indicators.oee'
    _columns = {
        'name': fields.char('Name', size=255, required=True),
        'line_ids': fields.one2many('mrp.indicators.oee.line', 'indicator_id', 'Lines'),
        'line_summary_by_workcenter_ids': fields.one2many(
            'mrp.indicators.oee.summary', 'indicator_id', 'Summary by workcenter',
            domain=[('summary_type', 'in', ('workcenter', 'total'))]),
        'line_summary_by_product_ids': fields.one2many(
            'mrp.indicators.oee.summary', 'indicator_id', 'Summary by product',
            domain=[('summary_type', 'in', ('product', 'total'))]),
        'date': fields.date('Date'),
        'user_id': fields.many2one('res.users', 'User'),
        'company_id': fields.many2one('res.company', 'Company'),
        'report_name': fields.char('Report', size=255)
    }
    _order = 'date desc, id desc'


class mrp_indicators_oee_line(orm.Model):
    _name = 'mrp.indicators.oee.line'
    _columns = {
        'name': fields.char('Name', size=255, required=True),
        'date': fields.date('Date'),
        'workcenter_id': fields.many2one('mrp.workcenter', 'Workcenter'),
        'production_id': fields.many2one('mrp.production', 'Production', select=True),
        'qty': fields.float('Qty', digits_compute=dp.get_precision('Product Unit of Measure'), required=True),
        'qty_scraps': fields.float('Scraps', digits_compute=dp.get_precision('Product Unit of Measure')),
        'qty_good': fields.float('Real qty', digits_compute=dp.get_precision('Product Unit of Measure')),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'stop_time': fields.float('Stop time'),
        'real_time': fields.float('Real time'),
        'tic_time': fields.float('TiC time'),
        'time_start': fields.float('Time start'),
        'time_stop': fields.float('Time stop'),
        'gasoleo_start': fields.float('Gasoleo start'),
        'gasoleo_stop': fields.float('Gasoleo stop'),
        'oee': fields.float('OEE'),
        'availability': fields.float('Availability'),
        'performance': fields.float('Performance'),
        'quality': fields.float('Quality'),
        'indicator_id': fields.many2one('mrp.indicators.oee', 'Indicator', ondelete='cascade', required=True)
    }


class mrp_indicators_oee_summary(orm.Model):
    _name = 'mrp.indicators.oee.summary'
    _order = 'indicator_id, workcenter_id, product_id'
    _columns = {
        'name': fields.char('Name', size=255, required=True),
        'workcenter_id': fields.many2one('mrp.workcenter', 'Workcenter'),
        'product_id': fields.many2one('product.product', 'Product'),
        'oee': fields.float('OEE'),
        'availability': fields.float('Availability'),
        'performance': fields.float('Performance'),
        'quality': fields.float('Quality'),
        'summary_type': fields.selection([
            ('workcenter', "Workcenter"),
            ('product', 'Product'),
            ('total', 'Total'),
           ], 'Summary type', required=True),
        'indicator_id': fields.many2one('mrp.indicators.oee', 'Indicator', ondelete='cascade', required=True)
    }
    _defaults = {
        'summary_type': 'workcenter'
    }


class mrp_indicators_scrap(orm.Model):
    _name = 'mrp.indicators.scrap'
    _columns = {
        'name': fields.char('Name', size=255, required=True),
        'line_ids': fields.one2many('mrp.indicators.scrap.line', 'indicator_id', 'Lines'),
        'date': fields.date('Date'),
        'user_id': fields.many2one('res.users', 'User'),
        'company_id': fields.many2one('res.company', 'Company'),
        'report_name': fields.char('Report', size=255)
    }
    _order = 'date desc, id desc'


class mrp_indicators_scrap_line(orm.Model):
    _name = 'mrp.indicators.scrap.line'
    _columns = {
        'name': fields.char('Name', size=255, required=True),
        'date': fields.date('Date'),
        'production_id': fields.many2one('mrp.production', 'Production', select=True),
        'product_id': fields.many2one('product.product', 'Product', select=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure'),
        'real_qty': fields.float('Real qty', digits_compute=dp.get_precision('Product Unit of Measure')),
        'theorical_qty':fields.float('Total qty.', digits_compute=dp.get_precision('Product Unit of Measure')),
        'scrap_qty': fields.float('Scrap qty.', digits_compute=dp.get_precision('Product Unit of Measure')),
        'real_cost': fields.float('Real cost', digits_compute=dp.get_precision('Product Unit of Measure')),
        'theorical_cost': fields.float('Theorical cost', digits_compute=dp.get_precision('Product Unit of Measure')),
        'scrap_cost': fields.float('Scrap', digits_compute=dp.get_precision('Product Unit of Measure'), select=True),
        'usage_cost': fields.float('Usage', digits_compute=dp.get_precision('Product Unit of Measure'), select=True),
        'indicator_id': fields.many2one('mrp.indicators.scrap', 'Indicator', ondelete='cascade', required=True),
    }


class mrp_indicators_overweight(orm.Model):
    _name = 'mrp.indicators.overweight'
    _columns = {
        'name': fields.char('Name', size=255, required=True),
        'line_ids': fields.one2many('mrp.indicators.overweight.line', 'indicator_id', 'Lines'),
        'line_summary_ids': fields.one2many('mrp.indicators.overweight.summary', 'indicator_id', 'Summary'),
        'date': fields.date('Date'),
        'user_id': fields.many2one('res.users', 'User'),
        'company_id': fields.many2one('res.company', 'Company'),
        'report_name': fields.char('Report', size=255)
    }
    _order = 'date desc, id desc'


class mrp_indicators_overweight_line(orm.Model):
    _name = 'mrp.indicators.overweight.line'
    _columns = {
        'name': fields.char('Name', size=255, required=True),
        'date': fields.date('Date'),
        'production_id': fields.many2one('mrp.production', 'Production', select=True),
        'workcenter_id': fields.many2one('mrp.workcenter', 'Workcenter'),
        'product_id': fields.many2one('product.product', 'Product', select=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure'),
        'qty_nominal': fields.float('Qty nominal', digits_compute=dp.get_precision('Product Unit of Measure')),
        'qty_consumed': fields.float('Qty consumed', digits_compute=dp.get_precision('Product Unit of Measure')),
        'overweight': fields.float('Overweight (%)'),
        'overweight_abs': fields.float('Overweight Abs'),
        'indicator_id': fields.many2one('mrp.indicators.overweight', 'Indicator', ondelete='cascade', required=True),
    }


class mrp_indicators_overweight_summary(orm.Model):
    _name = 'mrp.indicators.overweight.summary'
    _columns = {
        'name': fields.char('Name', size=255, required=True),
        'workcenter_id': fields.many2one('mrp.workcenter', 'Workcenter'),
        'qty_nominal': fields.float('Qty nominal', digits_compute=dp.get_precision('Product Unit of Measure')),
        'qty_consumed': fields.float('Qty consumed', digits_compute=dp.get_precision('Product Unit of Measure')),
        'overweight': fields.float('Overweight (%)'),
        'overweight_abs': fields.float('Overweight Abs'),
        'indicator_id': fields.many2one('mrp.indicators.overweight', 'Indicator', ondelete='cascade', required=True)
    }
