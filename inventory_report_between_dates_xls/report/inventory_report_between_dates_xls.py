# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2016 QUIVAL, S.A. All Rights Reserved
#    $Pedro Gómez Campos$ <pegomez@elnogal.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
import xlwt
from openerp.addons.report_xls.report_xls import report_xls
from datetime import datetime
from openerp.report import report_sxw
from openerp.tools.translate import _


_ir_translation_name = 'inventory_report_between_dates.xls'


class InventoryReportBetweenDatesXlsParser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(InventoryReportBetweenDatesXlsParser, self).__init__(cr, uid, name,
                                                     context=context)

        self.context = context
        self.localcontext.update({'datetime': datetime, '_': _})


class InventoryReportBetweenDatesXls(report_xls):
    column_sizes = [8, 10, 40, 15, 15, 15, 15, 15, 15, 20, 15, 15, 15, 15]

    def __init__(self, name, table, rml=False, parser=False,
                 header=True, store=False):
        super(InventoryReportBetweenDatesXls, self).\
            __init__(name, table, rml, parser, header, store)

        _xs = self.xls_styles
        rh_cell_format = _xs['bold'] + _xs['borders_all']
        # lines
        aml_cell_format = _xs['borders_all']
        self.aml_cell_style = xlwt.easyxf(aml_cell_format)
        self.aml_cell_style_center = xlwt.easyxf(aml_cell_format +
                                                 _xs['center'])
        self.aml_cell_style_date = \
            xlwt.easyxf(aml_cell_format + _xs['left'],
                        num_format_str=report_xls.date_format)
        self.aml_cell_style_decimal = \
            xlwt.easyxf(aml_cell_format + _xs['right'],
                        num_format_str=report_xls.decimal_format)
        self.rh_cell_style = xlwt.easyxf(rh_cell_format)

    def global_initializations(self, wb, _p, xlwt, _xs, objects, data):
        # this procedure will initialise variables and Excel cell styles and
        # return them as global ones
        self.ws = wb.add_sheet(_("Inventario entre fechas"))
        self.nbr_columns = 7
        # Tytle style
        self.style_font12 = xlwt.easyxf(_xs['xls_title'] + _xs['center'])
        # Header Style
        self.style_bold_blue_center = xlwt.easyxf(
            _xs['bold'] + _xs['fill_blue'] + _xs['borders_all'] +
            _xs['center'])
        self.report_date = objects.date_from

    def print_title(self, objects, row_pos):
        report_name = ' // '.join(["INVENTARIO ENTRE FECHAS", objects.date_from + ' a ' +
                                 objects.date_to])
        c_specs = [('report_name', self.nbr_columns, 0, 'text', report_name)]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            self.ws, row_pos, row_data, row_style=self.style_font12)
        return row_pos

    # send an empty row to the Excel document
    def print_empty_row(self, row_pos):
        c_sizes = self.column_sizes
        c_specs = [('empty%s' % i, 1, c_sizes[i], 'text', None)
                   for i in range(0, len(c_sizes))]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            self.ws, row_pos, row_data, set_column_size=True)
        return row_pos

    def print_header_titles(self, row_pos):
        style1 = self.style_bold_blue_center
        # PART 1
        c_specs = [
            ('a', 1, 0, 'text', _('id'), None, style1),
            ('b', 1, 0, 'text', _('Código'), None, style1),
            ('c', 1, 0, 'text', _('Descripción'), None, style1),
            ('d', 1, 0, 'text', _('Stock inicial'), None, style1),
            ('e', 1, 0, 'text', _('Entradas'), None, style1),
            ('f', 1, 0, 'text', _('Salidas'), None, style1),
            ('g', 1, 0, 'text', _('Stock final'), None, style1),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(self.ws, row_pos, row_data)
        return row_pos

    def _print_report_values(self, data, row_pos):
        for acc_name in data:
            val = data[acc_name]
            c_specs = [
                ('a', 1, 0, 'text', acc_name, None, None),
                ('b', 1, 0, 'text', val['code'], None, None),
                ('c', 1, 0, 'text', val['name'], None, None),
                ('d', 1, 0, 'number', str(round(val['qty_from'], 2)), None, None),
                ('e', 1, 0, 'number', str(round(val['qty_in'], 2)), None, None),
                ('f', 1, 0, 'number', str(round(val['qty_out'], 2)), None, None),
                ('g', 1, 0, 'number', str(round(val['qty_to'], 2)), None, None),
            ]
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(self.ws, row_pos, row_data)
        return row_pos

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        # Initializations
        self.global_initializations(wb, _p, xlwt, _xs, objects, data)
        
        row_pos = 0
        # Report Title
        row_pos = self.print_title(objects, row_pos)
        # Print empty row to define column sizes
        row_pos = self.print_empty_row(row_pos)
        # Headers
        row_pos = self.print_header_titles(row_pos)
        # Values
        row_pos = self._print_report_values(data, row_pos)


InventoryReportBetweenDatesXls('report.inventory_report_between_dates_xls',
                 'inventory.report.between.dates.xls.wzd',
                 parser=InventoryReportBetweenDatesXlsParser)
