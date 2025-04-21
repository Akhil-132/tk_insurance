from odoo import api, fields, models
import base64
import csv
import io
import chardet

class BrandName(models.Model):
    _name = 'insurance.brand.name'
    _description = 'Insurance Brand Name'
    _rec_name = 'name'

    name = fields.Char(string="Brand Name", required=True, translate=True)
    brand_models = fields.One2many('insurance.brand.model', 'brand_name_id', string='Brand Models')


class BrandModel(models.Model):
    _name = 'insurance.brand.model'
    _description = 'Insurance Brand Model'
    _rec_name = 'name'

    name = fields.Char(string="Brand Model", required=True, translate=True)
    brand_name_id = fields.Many2one('insurance.brand.name', string="Brand Name", required=True, ondelete='cascade')
    brand_variants = fields.One2many('insurance.brand.variant', 'brand_model_id', string='Brand Variants')
    brand_variants_display = fields.Char(
        string="Brand Variants",
        compute="_compute_brand_variants_display",
        store=True
    )

    @api.depends('brand_variants')
    def _compute_brand_variants_display(self):
        """Compute the brand variants as a comma-separated string."""
        for record in self:
            record.brand_variants_display = ', '.join(record.brand_variants.mapped('name')) if record.brand_variants else "No Variants"

    _sql_constraints = [
        ('unique_model_per_brand', 'UNIQUE(name, brand_name_id)', 'Model must be unique within a brand!')
    ]


class BrandVariant(models.Model):
    _name = 'insurance.brand.variant'
    _description = 'Insurance Brand Variant'
    _rec_name = 'name'

    name = fields.Char(string="Brand Variant", required=True, translate=True)
    brand_model_id = fields.Many2one('insurance.brand.model', string="Brand Model", required=True, ondelete='cascade')

    _sql_constraints = [
        ('unique_variant_per_model', 'UNIQUE(name, brand_model_id)', 'Variant must be unique within a model!')
    ]

class InsuranceBrandUpload(models.Model):
    _name = 'insurance.brand.upload'
    _description = 'Upload Insurance Brands, Models, and Variants'

    name = fields.Char(string="Name")
    upload_file = fields.Binary(string="Upload CSV File", required=True)
    upload_file_name = fields.Char(string="File Name")


    def process_file(self):
        """Process uploaded CSV file and create brand, model, and variant records."""
        if not self.upload_file:
            return

        file_data = base64.b64decode(self.upload_file)

        # Detect encoding
        raw_data = file_data[:10000]  # Analyze only the first 10KB for performance
        detected = chardet.detect(raw_data)
        detected_encoding = detected["encoding"] if detected["confidence"] > 0.5 else "utf-8"

        # Try decoding with detected encoding
        try:
            file_content = file_data.decode(detected_encoding)
        except UnicodeDecodeError:
            file_content = file_data.decode("ISO-8859-1")  # Fallback to Latin-1

        # Remove null bytes
        file_content = file_content.replace("\x00", "")

        csv_data = io.StringIO(file_content, newline="")
        csv_reader = csv.reader(csv_data, delimiter=',', quotechar='"')

        # Skip header row
        next(csv_reader, None)

        for row in csv_reader:
            if len(row) < 3:
                continue  # Skip rows with insufficient data

            brand_name, model_name, variant_name = row[:3]

            # Ensure names are properly stripped and cleaned
            brand_name = brand_name.strip()
            model_name = model_name.strip()
            variant_name = variant_name.strip()

            # Create or get brand
            brand = self.env['insurance.brand.name'].search([('name', '=', brand_name)], limit=1)
            if not brand:
                brand = self.env['insurance.brand.name'].create({'name': brand_name})

            # Create or get model under the brand
            model = self.env['insurance.brand.model'].search([
                ('name', '=', model_name),
                ('brand_name_id', '=', brand.id)
            ], limit=1)
            if not model:
                model = self.env['insurance.brand.model'].create({
                    'name': model_name,
                    'brand_name_id': brand.id
                })

            # Create or get variant under the model
            variant = self.env['insurance.brand.variant'].search([
                ('name', '=', variant_name),
                ('brand_model_id', '=', model.id)
            ], limit=1)
            if not variant:
                self.env['insurance.brand.variant'].create({
                    'name': variant_name,
                    'brand_model_id': model.id
                })

        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'File Processed Successfully',
                'type': 'rainbow_man',
            }
        }




