# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Site.website'
        db.delete_column('registrations_site', 'website')

        # Deleting field 'Site.fax'
        db.delete_column('registrations_site', 'fax')

        # Deleting field 'Site.phone'
        db.delete_column('registrations_site', 'phone')

        # Deleting field 'Site.altemail'
        db.delete_column('registrations_site', 'altemail')

        # Deleting field 'Site.altphone'
        db.delete_column('registrations_site', 'altphone')

        # Deleting field 'Site.contact'
        db.delete_column('registrations_site', 'contact')

        # Deleting field 'Site.email'
        db.delete_column('registrations_site', 'email')


    def backwards(self, orm):
        # Adding field 'Site.website'
        db.add_column('registrations_site', 'website',
                      self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Site.fax'
        db.add_column('registrations_site', 'fax',
                      self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Site.phone'
        db.add_column('registrations_site', 'phone',
                      self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Site.altemail'
        raise RuntimeError("Cannot reverse this migration. 'Site.altemail' and its values cannot be restored.")
        # Adding field 'Site.altphone'
        db.add_column('registrations_site', 'altphone',
                      self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Site.contact'
        db.add_column('registrations_site', 'contact',
                      self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Site.email'
        db.add_column('registrations_site', 'email',
                      self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True),
                      keep_default=False)


    models = {
        'registrations.container': {
            'Meta': {'object_name': 'Container'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quantity': ('django.db.models.fields.FloatField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'})
        },
        'registrations.context': {
            'Meta': {'object_name': 'Context'},
            'budget': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Country']"}),
            'freight': ('django.db.models.fields.FloatField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'gni_per_capita': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'import_duty': ('django.db.models.fields.FloatField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'local_preference': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'nmpa_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'nmpa_status': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'nmpa_website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'nmra_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'nmra_website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'payment_terms': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'population': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'pspa_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'pspa_website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Source']"}),
            'tender_currencies': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'tender_time': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'registrations.country': {
            'Meta': {'object_name': 'Country'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        'registrations.currency': {
            'Meta': {'object_name': 'Currency'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'registrations.dosageform': {
            'Meta': {'object_name': 'DosageForm'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        'registrations.incoterm': {
            'Meta': {'object_name': 'Incoterm'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '3'})
        },
        'registrations.ingredient': {
            'Meta': {'ordering': "('inn__name',)", 'object_name': 'Ingredient'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inn': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.INN']"}),
            'medicine': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Medicine']"}),
            'strength': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        'registrations.inn': {
            'Meta': {'object_name': 'INN'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'registrations.manufacturer': {
            'Meta': {'object_name': 'Manufacturer'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Country']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'registrations.medicine': {
            'Meta': {'object_name': 'Medicine'},
            'dosageform': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.DosageForm']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ingredients': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['registrations.INN']", 'through': "orm['registrations.Ingredient']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        'registrations.mshprice': {
            'Meta': {'object_name': 'MSHPrice'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'medicine': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['registrations.Medicine']", 'unique': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {})
        },
        'registrations.pack': {
            'Meta': {'object_name': 'Pack'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'registrations.packsize': {
            'Meta': {'object_name': 'PackSize'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pack': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Pack']", 'null': 'True', 'blank': 'True'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {})
        },
        'registrations.procurement': {
            'Meta': {'object_name': 'Procurement'},
            'container': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Container']"}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Country']"}),
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Currency']"}),
            'end_date': ('django.db.models.fields.DateField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incoterm': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Incoterm']"}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'packsize': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Product']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Source']"}),
            'start_date': ('django.db.models.fields.DateField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'supplier': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Supplier']", 'null': 'True', 'blank': 'True'}),
            'volume': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'registrations.product': {
            'Meta': {'object_name': 'Product'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Manufacturer']", 'null': 'True'}),
            'medicine': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Medicine']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Site']", 'null': 'True', 'blank': 'True'})
        },
        'registrations.registration': {
            'Meta': {'object_name': 'Registration'},
            'application': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Country']"}),
            'expiry': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Site']", 'null': 'True', 'blank': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Product']"}),
            'registered': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Source']"}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'supplier': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Supplier']", 'null': 'True', 'blank': 'True'})
        },
        'registrations.site': {
            'Meta': {'object_name': 'Site'},
            'address': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Country']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Manufacturer']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'registrations.source': {
            'Meta': {'object_name': 'Source'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'registrations.supplier': {
            'Meta': {'object_name': 'Supplier'},
            'address': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'altemail': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'altphone': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'authorized': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contact': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Country']", 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Manufacturer']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['registrations']