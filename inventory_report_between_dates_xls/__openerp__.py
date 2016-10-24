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
{
    "name": "Inventory Report Between Dates XLS",
    "summary": "Inventory Report Between Dates",
    "version": "8.0.1.0.0",
    "category": "Inventory, Logistic, Storage",
    "website": "https://www.elnogal.com",
    "author": "Pedro Gómez",
    "license": "AGPL-3",
    "installable": True,
    "depends" : [
        'base',
        'stock',
        'report_xls',
    ],
    "data": [
        "wizard/inventory_report_between_dates_xls_wzd_view.xml",
        "report/inventory_report_between_dates.xml"
    ],
}
