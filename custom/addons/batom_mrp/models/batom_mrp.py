# -*- coding: utf-8 -*-
# Copyright <2016> <Batom Co., Ltd.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

class BatomMrpBom(models.Model):
     #_name = 'batom.mrp.bom'
     _inherit = 'mrp.bom'
     
     x_version_description = fields.Char('Version Description')
