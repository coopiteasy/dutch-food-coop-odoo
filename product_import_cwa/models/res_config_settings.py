# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_ftp_import = fields.Boolean(
        'Enable CWA FTP Import',
        config_parameter='cwa_enable_ftp_import',
        default=False
    )
    cwa_ftp_address = fields.Char(
        'FTP Address', config_parameter='cwa_ftp_address', default=''
    )
    cwa_ftp_username = fields.Char(
        'Username', config_parameter='cwa_ftp_username', default=''
    )
    cwa_ftp_password = fields.Char(
        'Password', config_parameter='cwa_ftp_password', default=''
    )

