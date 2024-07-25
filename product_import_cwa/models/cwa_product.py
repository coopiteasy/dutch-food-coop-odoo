# -*- coding: utf-8 -*-

import hashlib
from lxml import etree
from odoo import models, fields, api, _, tools
import os
import ftplib
from .utils import PRESENCE_SELECTION, YESNO_SELECTION
from .utils import split_data
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)

CHUNKSIZE = 50

# Which fields to load from XML
FIELDS_TO_LOAD = (
    'eancode',
    'omschrijving',
    'weegschaalartikel',
    'wichtartikel',
    'pluartikel',
    'inhoud',
    'eenheid',
    'verpakkingce',
    'merk',
    'kwaliteit',
    'btw',
    'cblcode',
    'bestelnummer',
    'proefdiervrij',
    'vegetarisch',
    'veganistisch',
    'rauwemelk',
    'inkoopprijs',
    'consumentenprijs',
    'ingangsdatum',
    'herkomst',
    'ingredienten',
    'statiegeld',
    'kassaomschrijving',
    'plucode',
    'sve',
    'status',
    'keurmerkbio',
    'keurmerkoverig',
    'herkomstregio',
    'aantaldagenhoudbaar',
    'bewaartemperatuur',
    'gebruikstips',
    'lengte',
    'breedte',
    'hoogte',
    'code',
    'd204',
    'd209',
    'd210',
    'd212',
    'd213',
    'd214',
    'd234',
    'd215',
    'd239',
    'd216',
    'd217',
    'd217b',
    'd220',
    'd221',
    'd221b',
    'd222',
    'd223',
    'd236',
    'd235',
    'd238',
    'd238b',
    'd225',
    'd226',
    'd228',
    'd230',
    'd232',
    'd237',
    'd240',
    'd241',
    'd242',
    'pos_categ_id',
    'leveranciernummer',
    (None, 'unique_id'),
    (None, 'hash'),
)


class CwaProduct(models.Model):
    _name = 'cwa.product'
    _description = 'CWA product'

    state = fields.Selection([
        ('new', 'New'),
        ('imported', 'Imported'),
        ], default='new')
    name = fields.Char("Product name", related='omschrijving')
    vendor_id = fields.Many2one(
        'res.partner', 'Leverancier', compute='_compute_vendor_id',
        search='_search_vendor_id', help="Vendor of this product")
    unique_id = fields.Char(index=True)
    eancode = fields.Char(help="EAN code")
    weegschaalartikel = fields.Boolean()
    wichtartikel = fields.Boolean()
    pluartikel = fields.Boolean()
    inhoud = fields.Char(help="Inhoud van de verpakking.")
    eenheid = fields.Char(help="Eenheid van de inhoud.")
    verpakkingce = fields.Char(help="Verpakking van consumenteneenheid.")
    merk = fields.Char(help="merk.")
    kwaliteit = fields.Char(help="Kwaliteitsaanduiding.")
    btw = fields.Char(help="BTW percentage 0, 6 of 21")
    cblcode = fields.Char(help="cblcode")
    leveranciernummer = fields.Char(help="Nummer van de leverancier.")
    bestelnummer = fields.Char(
        help="Bestelnummer van artikel bij leverancier.")
    proefdiervrij = fields.Selection(YESNO_SELECTION)
    vegetarisch = fields.Selection(YESNO_SELECTION)
    veganistisch = fields.Selection(YESNO_SELECTION)
    rauwemelk = fields.Selection(YESNO_SELECTION)
    inkoopprijs = fields.Float('Inkoopprijs', help="inkoopprijs")
    consumentenprijs = fields.Float('Adviesprijs', help="consumentenprijs")
    ingangsdatum = fields.Date(help="Ingangsdatum van product")
    herkomst = fields.Char(help="Land van herkomst in vorm ISO 3166 code.")
    ingredienten = fields.Text(help="Beschrijving van de ingredienten.")
    statiegeld = fields.Float(help="Statiegeldbedrag.")
    omschrijving = fields.Char(
        help="Omschrijving van het product")
    kassaomschrijving = fields.Char(
        help="Korte omschrijving van het product tbv de kassa")
    plucode = fields.Char(help="4-cijferige plucode.")
    sve = fields.Char(help="Standaard verpakkingseenheid bij leverancier.")
    status = fields.Char(help="Mogelijke waarden: Actief/Non Actief/Gesaneerd")
    keurmerkbio = fields.Char(help="keurmerkbio")
    keurmerkoverig = fields.Char(help="keurmerkoverig")
    herkomstregio = fields.Char(help="Regio van herkomst")
    aantaldagenhoudbaar = fields.Char(help="Aantal dagen houdbaar")
    bewaartemperatuur = fields.Char(help="bewaartemperatuur")
    gebruikstips = fields.Char(help="gebruikstips")
    lengte = fields.Char(help="lengte")
    breedte = fields.Char(help="breedte")
    hoogte = fields.Char(help="hoogte")
    code = fields.Char(help="code")
    d204 = fields.Selection(PRESENCE_SELECTION, help="Cacao")
    d209 = fields.Selection(PRESENCE_SELECTION, help="Glutamaat")
    d210 = fields.Selection(PRESENCE_SELECTION, help="Gluten")
    d212 = fields.Selection(PRESENCE_SELECTION, help="Ei")
    d213 = fields.Selection(PRESENCE_SELECTION, help="Kip")
    d214 = fields.Selection(PRESENCE_SELECTION, help="Melk")
    d234 = fields.Selection(PRESENCE_SELECTION, help="Koriander")
    d215 = fields.Selection(PRESENCE_SELECTION, help="Lactose")
    d239 = fields.Selection(PRESENCE_SELECTION, help="Lupine")
    d216 = fields.Selection(PRESENCE_SELECTION, help="Mais")
    d217 = fields.Selection(PRESENCE_SELECTION, help="Noten")
    d217b = fields.Selection(PRESENCE_SELECTION, help="Notenolie")
    d220 = fields.Selection(PRESENCE_SELECTION, help="Peulvruchten")
    d221 = fields.Selection(PRESENCE_SELECTION, help="Pinda")
    d221b = fields.Selection(PRESENCE_SELECTION, help="Pindaolie")
    d222 = fields.Selection(PRESENCE_SELECTION, help="Rogge")
    d223 = fields.Selection(PRESENCE_SELECTION, help="Rundvlees")
    d236 = fields.Selection(PRESENCE_SELECTION, help="Schaaldieren")
    d235 = fields.Selection(PRESENCE_SELECTION, help="Selderij")
    d238 = fields.Selection(PRESENCE_SELECTION, help="Sesam")
    d238b = fields.Selection(PRESENCE_SELECTION, help="Sesamolie")
    d225 = fields.Selection(PRESENCE_SELECTION, help="Soja")
    d226 = fields.Selection(PRESENCE_SELECTION, help="Soja-olie")
    d228 = fields.Selection(PRESENCE_SELECTION, help="Sulfiet")
    d230 = fields.Selection(PRESENCE_SELECTION, help="Tarwe")
    d232 = fields.Selection(PRESENCE_SELECTION, help="Varkensvlees")
    d237 = fields.Selection(PRESENCE_SELECTION, help="Vis")
    d240 = fields.Selection(PRESENCE_SELECTION, help="Wortel")
    d241 = fields.Selection(PRESENCE_SELECTION, help="Mosterd")
    d242 = fields.Selection(PRESENCE_SELECTION, help="Weekdieren")
    pos_categ_id = fields.Char(
        'NOT A REFERENCE', help="Not a reference field, just a char field.")
    hash = fields.Char(required=True)

    @api.model
    def parse_from_xml(self, prod_file):
        root = etree.parse(prod_file).getroot()
        load_values = []
        update_records = []

        # make a dict with existing products by unique_id
        cur_unique_ids = set()
        records = self.env['cwa.product'].search([]) \
            .read(['unique_id', 'hash'])
        hash_dict = {}
        for record in records:
            cur_unique_ids.add(record['unique_id'])
            hash_dict[record['unique_id']] = record['hash']

        # determine allowed source tags
        # determine list of destination fields
        load_tags = []
        load_fields = []
        for rec in FIELDS_TO_LOAD:
            if isinstance(rec, tuple):
                if rec[0]:
                    load_tags.append(rec[0])
                if rec[1]:
                    load_fields.append(rec[1])
            else:
                load_tags.append(rec)
                load_fields.append(rec)

        new_unique_ids = set()
        for product in root.iter('product'):
            # copy full XML record to dict
            temp_dict = {}
            for item in product:
                temp_dict[item.tag] = item.text if item.text else None

            # decide which ones to load
            load_dict = {}
            for tag, value in temp_dict.items():
                if tag not in load_tags:
                    _logger.warning('Ignoring unknown tag: %s', tag)
                    continue

                # load prices as floats
                elif tag in ('consumentenprijs', 'inkoopprijs'):
                    load_dict[tag] = "{0:.2f}".format(float(value))

                elif tag == 'verpakkingce':
                    if value:
                        load_dict[tag] = value.upper()
                    # else:
                    #     load_dict[tag] = 'STUKS'

                # load yes/no selections
                elif tag in ('proefdiervrij', 'vegetarisch',
                             'veganistisch', 'rauwemelk'):
                    if value in ['0', '1', '2']:
                        load_dict[tag] = value
                    else:
                        load_dict[tag] = '0'

                # load booleans
                elif tag in ('weegschaalartikel', 'pluartikel',
                             'wichtartikel'):
                    if value == '1':
                        load_dict[tag] = 'true'
                    else:
                        load_dict[tag] = 'false'

                elif tag == 'omschrijving':
                    load_dict[tag] = value.upper()

                else:
                    load_dict[tag] = value.upper() if value else None

            # create a hash from the recs to load
            _hash = hashlib.md5()
            for key, value in load_dict.items():
                _hash.update(key.encode('utf-8'))
                _hash.update(str(value).encode('utf-8'))
            new_hash = _hash.hexdigest()
            load_dict['hash'] = new_hash

            # create the unique id for this record
            unique_id = '%s-%s' % (
                temp_dict['leveranciernummer'],
                temp_dict['bestelnummer']
            )
            load_dict['unique_id'] = unique_id
            new_unique_ids.add(unique_id)

            old_hash = hash_dict.get(unique_id, None)
            if old_hash:
                # record exists, update only when hash is different
                if old_hash != new_hash:
                    update_records.append(load_dict)
            else:
                # convert load_dict to a list and append to load_values
                load_list = [load_dict.get(name, None) for name in load_fields]
                load_values.append(load_list)

        delete_records = list(cur_unique_ids - new_unique_ids)

        return load_fields, load_values, update_records, delete_records

    @api.model
    def update_records(self, records, model):
        count = 0
        for record in records:
            rec = self.env[model].search([
                ('unique_id', '=', record['unique_id'])
            ])
            if rec:
                rec.write(record)
                count += 1
        return count

    @api.model
    def load_records(self, keys, data, model):
        data_chunks = split_data(data, split_size=CHUNKSIZE)
        count_successful = 0
        for data_subset in data_chunks:
            for attempt in range(5):
                use_fresh_cursor = self.env.context.get('new_cursor', False)
                with api.Environment.manage():
                    if use_fresh_cursor:
                        _logger.info('new cursor created')
                        new_cr = self.pool.cursor()
                        uid, context = self.env.uid, self.env.context
                        env = api.Environment(new_cr, uid, context)
                    else:
                        env = self.env

                    try:
                        x = env[model].load(keys, data_subset)
                        if len(x['messages']) > 0:
                            _logger.warning("attempt..%s" % attempt)
                            _logger.error(x)
                            continue
                        else:
                            _logger.warning("success..%s" % attempt)
                            if use_fresh_cursor:
                                env.cr.commit()
                            count_successful += len(x['ids'])
                            break

                    finally:
                        if use_fresh_cursor:
                            env.cr.close()

        return count_successful

    @api.model
    def delete_records(self, unique_ids, model):
        for unique_id in unique_ids:
            self.env[model].search([(
                'unique_id', '=', unique_id
            )]).unlink()
        return len(unique_ids)

    @api.model
    def import_xml_products(self, prod_file):
        if not prod_file:
            prod_file = self._get_prod_file_from_ftp()
        if not prod_file:
            _logger.error("XML file not found!")
            return

        keys, to_load, to_update, to_delete = self.parse_from_xml(prod_file)
        count = 0
        if to_load:
            count += self.load_records(keys, to_load, 'cwa.product')
        if to_update:
            count += self.update_records(to_update, 'cwa.product')
        if to_delete:
            count += self.delete_records(to_delete, 'cwa.product')

        supplierinfo = self.env['product.supplierinfo'].search([], limit=500)
        if supplierinfo:  # Only compare prices if we have records
            supplierinfo.compare_prices()
        return count

    @api.model
    def import_demo_xml_products(self):
        path = os.path.dirname(os.path.realpath(__file__))
        prod_file = os.path.join(path, '../tests/data/products_test.xml')
        self.import_xml_products(prod_file)

    def to_product(self):
        """
        This is the main CWA import function.
        It imports a CWA product to a product.supplierinfo
        record, then couples to a product.template.
        If it cannot decode the CWA product well, it throws
        a ValidationError.
        """
        self.ensure_one()

        try:
            # product.supplierinfo values
            if not self.vendor_id:
                raise ValidationError(
                    _('Uknown vendor for this product. Fill the vendor first'))

            supplier_dict = {
                'cwa': True,
                'unique_id': self.unique_id,
                'eancode': self.eancode,
                'weegschaalartikel': self.weegschaalartikel,
                'pluartikel': self.pluartikel,
                'inhoud': self.inhoud,
                'eenheid': self.eenheid,
                'verpakkingce': self.verpakkingce,
                'merk': self.merk,
                'kwaliteit': self.kwaliteit,
                'btw': self.btw,
                'cblcode': self.cblcode,
                'bestelnummer': self.bestelnummer,
                'leveranciernummer': self.leveranciernummer,
                'proefdiervrij': self.proefdiervrij,
                'vegetarisch': self.vegetarisch,
                'veganistisch': self.veganistisch,
                'rauwemelk': self.rauwemelk,
                'inkoopprijs': self.inkoopprijs,
                'consumentenprijs': self.consumentenprijs,
                'old_consumentenprijs': self.consumentenprijs,
                'ingangsdatum': self.ingangsdatum,
                'herkomst': self.herkomst,
                'ingredienten': self.ingredienten,
                'statiegeld': self.statiegeld,
                'kassaomschrijving': self.kassaomschrijving,
                'plucode': self.plucode,
                'sve': self.sve,
                'status': self.status,
                'keurmerkbio': self.keurmerkbio,
                'keurmerkoverig': self.keurmerkoverig,
                'herkomstregio': self.herkomstregio,
                'aantaldagenhoudbaar': self.aantaldagenhoudbaar,
                'bewaartemperatuur': self.bewaartemperatuur,
                'gebruikstips': self.gebruikstips,
                'lengte': self.lengte,
                'breedte': self.breedte,
                'hoogte': self.hoogte,
                'code': self.code,
                'd204': self.d204,
                'd209': self.d209,
                'd210': self.d210,
                'd212': self.d212,
                'd213': self.d213,
                'd214': self.d214,
                'd234': self.d234,
                'd215': self.d215,
                'd239': self.d239,
                'd216': self.d216,
                'd217': self.d217,
                'd217b': self.d217b,
                'd220': self.d220,
                'd221': self.d221,
                'd221b': self.d221b,
                'd222': self.d222,
                'd223': self.d223,
                'd236': self.d236,
                'd235': self.d235,
                'd238': self.d238,
                'd238b': self.d238b,
                'd225': self.d225,
                'd226': self.d226,
                'd228': self.d228,
                'd230': self.d230,
                'd232': self.d232,
                'd237': self.d237,
                'd240': self.d240,
                'd241': self.d241,
                'd242': self.d242,
                'pos_categ_id': self.pos_categ_id,
                'product_code': self.bestelnummer,
                'product_name': self.omschrijving,
                'price': self.inkoopprijs,
                'date_start': self.ingangsdatum,
                'name': self.vendor_id.id
            }

            # extra product.template values
            extra_prod_dict = {}

            # Translate standard unit of packaging
            if self.sve:
                supplier_dict['min_qty'] = "{0:.2f}".format(float(self.sve))

            # Translate brand
            brand = self.merk
            translated_brand = \
                self.env['cwa.product.brands'].get_translated(brand)
            if not translated_brand and not self.env.context.get('force'): # skip this if via force
                raise ValidationError(
                    _('Could not translate brand %s') % (brand,))
            else:
                extra_prod_dict['product_brand_id'] = translated_brand.destination_value.id

            # Translate uoms
            uom = self.eenheid
            translated_eenheid = \
                self.env['cwa.product.uom'].get_translated(uom)
            if not translated_eenheid and not self.env.context.get(
                    'force'):  # skip this if via force
                raise ValidationError(
                    _('Could not translate UoM %s') % (uom,))
            else:
                extra_prod_dict['uom_id'] = translated_eenheid.uom_id.id
                extra_prod_dict['uom_po_id'] = translated_eenheid.uom_po_id.id

            # Translate cblcodes - to internal_category & pos_category
            cblcode = self.cblcode
            translated_cblcode = \
                self.env['cwa.product.cblcode'].get_translated(cblcode)
            if not translated_cblcode and not self.env.context.get(
                    'force'):  # skip this if via force
                msg = _('Cannot translate CBL code %s into product categories.') % (
                    self.cblcode, )
                raise ValidationError(msg)
            else:
                extra_prod_dict['categ_id'] = translated_cblcode.internal_category.id
                extra_prod_dict['pos_categ_id'] = translated_cblcode.pos_category.id

            # Translate Quality
            quality = self.kwaliteit
            if quality:
                translated_quality = \
                    self.env['cwa.product.quality'].get_translated(quality)
                if not translated_quality and not self.env.context.get(
                        'force'):  # skip this if via force
                    raise ValidationError(
                        _('Could not translate Quality %s') % (quality,))
                else:
                    extra_prod_dict['kwaliteit'] = translated_quality.id
            else:
                extra_prod_dict['kwaliteit'] = self.env.ref(
                    'product_import_cwa.cwa_quality_afbak').id

            # BTW translations
            btw = self.btw
            if btw:
                translated_btw = self.env['cwa.vat.tax'].get_translated(btw)
                if not translated_btw and not self.env.context.get(
                        'force'):  # skip this if via force
                    raise ValidationError(
                        _('Could not get the tax translation for btw: %s') % (btw,))
                else:
                    extra_prod_dict['taxes_id'] = [(6, 0, translated_btw.sale_tax.ids)]
                    extra_prod_dict['supplier_taxes_id'] = [(6, 0, translated_btw.purchase_tax.ids)]

            # Search if a product with this EAN code already exists
            prod_obj = self.env['product.template']
            products_by_unique_code = prod_obj.search([
                ('unique_id', '=', self.unique_id)
            ])
            products_by_ean_code = self.eancode and prod_obj.search([
                ('eancode', '=', self.eancode)
            ])
            # Create new product if the eancode is missing
            if not products_by_unique_code and not products_by_ean_code:
                prod_dict = {
                    'unique_id': self.unique_id,
                    'eancode': self.eancode,
                    'barcode': self.eancode,
                    'name': self.omschrijving,
                    'standard_price': self.inkoopprijs,
                    'list_price': self.consumentenprijs,
                    'seller_ids': [(0, 0, supplier_dict)],
                    'kwaliteit': self.kwaliteit,
                    'available_in_pos': False,
                }
                prod_dict.update(extra_prod_dict)
                prod_obj.create(prod_dict)

            # Otherwise if this is a new supplier, add to existing product
            elif not products_by_unique_code and products_by_ean_code and not \
                    supplier_dict['name'] in products_by_ean_code.mapped('seller_ids.name.id'):
                products_by_ean_code[0].write({
                    'seller_ids': [(0, 0,  supplier_dict)]
                })
            elif products_by_unique_code and not supplier_dict['name'] in \
                    products_by_unique_code.mapped('seller_ids.name.id'):
                supplier_dict['sequence'] = 5  # give it least preference
                products_by_unique_code[0].write({
                    'seller_ids': [(0, 0, supplier_dict)]
                })
            # Otherwise throw an error, supplier/eancode already exists
            else:
                raise ValidationError(
                    _('A Product with same Leveranciernummer& Bestelnummer already imported'))
            self.write({'state': 'imported'})
        except ValidationError:
            if self.env.context.get('force'):
                pass
            else:
                raise
        return True

    @api.depends('leveranciernummer')
    def _compute_vendor_id(self):
        for this in self:
            supplier = self.env['cwa.product.suppliers'].search(
                [('leveranciernummer', '=',
                  this.leveranciernummer)]).res_partner_id
            this.vendor_id = supplier.id

    @api.model
    def _search_vendor_id(self, operator, value):
        pass

    def _get_prod_file_from_ftp(self):
        ir_config = self.env['ir.config_parameter'].sudo()
        config_address = tools.config.get('ftp_address', False)
        if ir_config.get_param('cwa_enable_ftp_import', default=False):
            host = ir_config.get_param('cwa_ftp_address')
            username = ir_config.get_param('cwa_ftp_username')
            passwd = ir_config.get_param('cwa_ftp_password')

        else:
            # Get credentials from the odoo.cfg
            host = config_address
            username = tools.config.get('ftp_username')
            passwd = tools.config.get('ftp_password')

        if not host or not username or not passwd:
            return

        tmp = False
        try:
            ftp_server = ftplib.FTP(host, username, passwd)
            ftp_server.encoding = "utf-8"
            root = 'VoorWinkel'
            # Go into the Root Directory
            ftp_server.cwd(root)
            files_in_dir = ftp_server.nlst()
            # ignore Actie files
            files_in_dir = [x for x in files_in_dir if 'Artikelen' in x]
            # pick the latest if there are files
            if not files_in_dir:
                _logger.error("Directory '%s' is empty!" % root)
                return
            remote = "/%s/%s" % (root, files_in_dir[-1])
            tmp = '/tmp/products_data.xml'
            with open(tmp, 'wb') as file:
                _logger.info("Downloading file: %s >>>> %s" % (remote, tmp))
                try:
                    ftp_server.retrbinary('RETR %s' % remote, file.write)
                    _logger.info(
                        "File successfully downloaded....proceed with Import!")
                except ftplib.error_perm as err:
                    _logger.error("Downloading Failed!!: %s" % err)
                    return

                ftp_server.quit()
        except ftplib.all_errors as err:
            _logger.error("Failed to Download from FTP: %s" % err)
        return tmp
