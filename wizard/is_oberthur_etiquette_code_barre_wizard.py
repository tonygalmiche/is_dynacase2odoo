# -*- coding: utf-8 -*-
import io
import base64
import logging
from markupsafe import Markup
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class IsOberthurEtiquetteCodeBarreWizard(models.TransientModel):
    _name = 'is.oberthur.etiquette.code.barre.wizard'
    _description = "Assistant d'impression d'étiquettes code-barres Oberthur"

    reference_coque = fields.Char(
        string="Référence de la coque 1ier Flux",
        required=True,
        default=lambda self: self._default_reference_coque(),
    )
    numero_chrono = fields.Integer(
        string="N° de Chrono de la 1ière Étiquette",
        required=True,
        default=lambda self: self._default_numero_chrono(),
    )
    nb_etiquettes = fields.Integer(
        string="Nombre d'étiquettes",
        required=True,
        default=33,
        help="Nombre total d'étiquettes à imprimer (33 par page : 3 colonnes x 11 lignes)",
    )
    afficher_bordure = fields.Boolean(
        string="Afficher les bordures des étiquettes",
        default=False,
    )
    afficher_bordure_page = fields.Boolean(
        string="Afficher la bordure de la page",
        default=False,
    )
    hauteur_etiquette = fields.Float(
        string="Hauteur étiquette (mm)",
        required=True,
        default=24.5,
        help="Hauteur de chaque étiquette en mm. Pour 11 lignes sur A4 avec marges 5mm : (297-5-0-(10*5))/11 ≈ 22mm",
    )
    # Type de rendu du code-barres dans le PDF :
    # - 'svg'      : Génération vectorielle via python-barcode (SVG encodé en base64 dans une balise <img>).
    #                Avantages : rendu net quelle que soit la résolution, bien lisible par les douchettes.
    #                Inconvénients : nécessite le package python-barcode installé sur le serveur.
    # - 'fonte'    : Utilise la fonte Libre Barcode 39 (fichier TTF dans static/src/fonts/).
    #                Avantages : pas de dépendance externe, rendu vectoriel natif.
    #                Inconvénients : la fonte doit être installée sur le serveur (système) pour que
    #                wkhtmltopdf puisse l'utiliser ; sinon le code-barres ne s'affiche pas correctement.
    #                Installation sur Debian 11 :
    #                  sudo cp /opt/odoo16/addons-perso/is_dynacase2odoo/static/src/fonts/LibreBarcode39-Regular.ttf /usr/share/fonts/truetype/
    #                  sudo chmod 644 /usr/share/fonts/truetype/LibreBarcode39-Regular.ttf
    #                  sudo fc-cache -fv
    #                  puis redémarrer Odoo.
    # - 'standard' : Image bitmap générée par le contrôleur Odoo standard (/report/barcode/Standard39/).
    #                Avantages : fonctionne sans aucune installation supplémentaire (natif Odoo).
    #                Inconvénients : rendu bitmap (pixelisé), moins net que les options vectorielles.
    type_code_barre = fields.Selection([
        ('svg', 'SVG vectoriel (net)'),
        ('fonte', 'Fonte Code 39'),
        ('standard', 'Standard (image)'),
    ], string="Type de code-barres", required=True, default='svg')

    def _default_reference_coque(self):
        return self.env['is.mem.var'].get(self.env.uid, 'oberthur_eti_reference_coque') or 'K0301A'

    def _default_numero_chrono(self):
        val = self.env['is.mem.var'].get(self.env.uid, 'oberthur_eti_numero_chrono')
        return int(val) if val else 1

    def action_imprimer(self):
        """Lance l'impression des étiquettes code-barres"""
        self.ensure_one()
        # Mémoriser les valeurs pour la prochaine utilisation
        mem_var = self.env['is.mem.var']
        mem_var.set(self.env.uid, 'oberthur_eti_reference_coque', self.reference_coque)
        mem_var.set(self.env.uid, 'oberthur_eti_numero_chrono', str(self.numero_chrono))
        # Préparer les données des étiquettes
        etiquettes = []
        for i in range(self.nb_etiquettes):
            numero = self.numero_chrono + i
            numero_str = str(numero).zfill(5)
            code = self.reference_coque + numero_str
            svg_data = ''
            if self.type_code_barre == 'svg':
                try:
                    import barcode
                    from barcode.writer import SVGWriter
                    Code39 = barcode.get_barcode_class('code39')
                    code39 = Code39(code, writer=SVGWriter(), add_checksum=False)
                    buffer = io.BytesIO()
                    code39.write(buffer, {'module_height': 13.0, 'module_width': 0.3, 'write_text': False, 'quiet_zone': 1.0})
                    svg_raw = buffer.getvalue().decode('utf-8')
                    # Extraire juste le contenu SVG (sans déclaration XML)
                    if '<?xml' in svg_raw:
                        svg_raw = svg_raw[svg_raw.index('<svg'):]
                    # Encoder en base64 pour utiliser dans une balise img
                    svg_b64 = base64.b64encode(svg_raw.encode('utf-8')).decode('utf-8')
                    svg_data = 'data:image/svg+xml;base64,' + svg_b64
                except Exception as e:
                    _logger.error("Erreur génération SVG pour %s: %s", code, e)
                    svg_data = ''
            _logger.info("## Code-barres pour %s (type=%s): %s", code, self.type_code_barre, str(svg_data)[:80] if svg_data else 'N/A')
            etiquettes.append({
                'code': code,
                'barcode': '*' + code + '*',
                #'barcode': code,
                'svg': svg_data,
            })

        # Regrouper par lignes de 3
        lignes = []
        for i in range(0, len(etiquettes), 3):
            ligne = etiquettes[i:i+3]
            # Compléter la ligne si moins de 3 étiquettes
            while len(ligne) < 3:
                ligne.append({'code': '', 'barcode': ''})
            lignes.append(ligne)

        # Regrouper par pages de 11 lignes
        pages = []
        for i in range(0, len(lignes), 11):
            pages.append(lignes[i:i+11])

        data = {
            'pages': pages,
            'reference_coque': self.reference_coque,
            'numero_chrono': self.numero_chrono,
            'afficher_bordure': self.afficher_bordure,
            'afficher_bordure_page': self.afficher_bordure_page,
            'hauteur_etiquette': self.hauteur_etiquette,
            'type_code_barre': self.type_code_barre,
        }
        return self.env.ref('is_dynacase2odoo.is_oberthur_etiquette_code_barre_report').report_action(self, data=data)


class IsOberthurEtiquetteCodeBarreReport(models.AbstractModel):
    _name = 'report.is_dynacase2odoo.report_is_oberthur_etiquette_code_barre'
    _description = "Rapport étiquettes code-barres Oberthur"

    @api.model
    def _get_report_values(self, docids, data=None):
        pages = data.get('pages', []) if data else []
        return {
            'doc_ids': docids,
            'doc_model': 'is.oberthur.etiquette.code.barre.wizard',
            'docs': self.env['is.oberthur.etiquette.code.barre.wizard'].browse(docids),
            'pages': pages,
            'afficher_bordure': data.get('afficher_bordure', False) if data else False,
            'afficher_bordure_page': data.get('afficher_bordure_page', False) if data else False,
            'hauteur_etiquette': data.get('hauteur_etiquette', 22.0) if data else 22.0,
            'type_code_barre': data.get('type_code_barre', 'svg') if data else 'svg',
        }
