# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Source'
        db.create_table('registrations_source', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('registrations', ['Source'])

        # Adding model 'Country'
        db.create_table('registrations_country', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=2)),
        ))
        db.send_create_signal('registrations', ['Country'])

        # Adding model 'Incoterm'
        db.create_table('registrations_incoterm', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('registrations', ['Incoterm'])

        # Adding model 'DosageForm'
        db.create_table('registrations_dosageform', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=16)),
        ))
        db.send_create_signal('registrations', ['DosageForm'])

        # Adding model 'INN'
        db.create_table('registrations_inn', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('registrations', ['INN'])

        # Adding model 'Medicine'
        db.create_table('registrations_medicine', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registrations.Source'])),
            ('dosageform', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registrations.DosageForm'])),
        ))
        db.send_create_signal('registrations', ['Medicine'])

        # Adding model 'Ingredient'
        db.create_table('registrations_ingredient', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('medicine', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registrations.Medicine'])),
            ('inn', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registrations.INN'])),
            ('strength', self.gf('django.db.models.fields.CharField')(max_length=16)),
        ))
        db.send_create_signal('registrations', ['Ingredient'])

        # Adding model 'Product'
        db.create_table('registrations_product', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registrations.Source'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('medicine', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registrations.Medicine'])),
        ))
        db.send_create_signal('registrations', ['Product'])

        # Adding model 'MSHPrice'
        db.create_table('registrations_mshprice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('medicine', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['registrations.Medicine'], unique=True)),
            ('price', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('registrations', ['MSHPrice'])

        # Adding model 'Manufacturer'
        db.create_table('registrations_manufacturer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registrations.Source'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registrations.Country'], null=True, blank=True)),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('registrations', ['Manufacturer'])

        # Adding model 'Site'
        db.create_table('registrations_site', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registrations.Source'])),
            ('manufacturer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registrations.Manufacturer'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('address', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registrations.Country'], null=True, blank=True)),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('contact', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True)),
            ('altphone', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True)),
            ('fax', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('altemail', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('prequalify', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('registrations', ['Site'])

        # Adding model 'Supplier'
        db.create_table('registrations_supplier', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registrations.Source'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('address', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registrations.Country'], null=True, blank=True)),
            ('manufacturer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registrations.Manufacturer'], null=True, blank=True)),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('contact', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True)),
            ('altphone', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True)),
            ('fax', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('altemail', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('prequalify', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('authorized', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('registrations', ['Supplier'])

        # Adding model 'Pack'
        db.create_table('registrations_pack', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('registrations', ['Pack'])

        # Adding model 'PackSize'
        db.create_table('registrations_packsize', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pack', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registrations.Pack'], null=True, blank=True)),
            ('registration', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registrations.Registration'])),
            ('quantity', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('registrations', ['PackSize'])

        # Adding model 'Registration'
        db.create_table('registrations_registration', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registrations.Source'])),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registrations.Country'])),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registrations.Product'])),
            ('manufacturer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registrations.Site'], null=True, blank=True)),
            ('supplier', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registrations.Supplier'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('application', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('registered', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('expiry', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('registrations', ['Registration'])

        # Adding model 'Procurement'
        db.create_table('registrations_procurement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registrations.Source'])),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registrations.Country'])),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registrations.Product'])),
            ('pack', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registrations.PackSize'], null=True, blank=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registrations.Site'], null=True, blank=True)),
            ('supplier', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registrations.Supplier'], null=True, blank=True)),
            ('incoterm', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registrations.Incoterm'])),
            ('price', self.gf('django.db.models.fields.FloatField')()),
            ('volume', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('period', self.gf('django.db.models.fields.IntegerField')(max_length=16, null=True, blank=True)),
            ('method', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('validity', self.gf('django.db.models.fields.DateField')(max_length=32, null=True, blank=True)),
        ))
        db.send_create_signal('registrations', ['Procurement'])

        # Adding model 'Context'
        db.create_table('registrations_context', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registrations.Source'])),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['registrations.Country'])),
            ('population', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('gni_per_capita', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('nmra_name', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('nmra_website', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('pspa_name', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('pspa_website', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('nmpa_name', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('nmpa_website', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('nmpa_status', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('budget', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('tender_time', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('tender_currencies', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('payment_terms', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('local_preference', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('import_duty', self.gf('django.db.models.fields.FloatField')(max_length=64, null=True, blank=True)),
            ('freight', self.gf('django.db.models.fields.FloatField')(max_length=64, null=True, blank=True)),
        ))
        db.send_create_signal('registrations', ['Context'])


    def backwards(self, orm):
        # Deleting model 'Source'
        db.delete_table('registrations_source')

        # Deleting model 'Country'
        db.delete_table('registrations_country')

        # Deleting model 'Incoterm'
        db.delete_table('registrations_incoterm')

        # Deleting model 'DosageForm'
        db.delete_table('registrations_dosageform')

        # Deleting model 'INN'
        db.delete_table('registrations_inn')

        # Deleting model 'Medicine'
        db.delete_table('registrations_medicine')

        # Deleting model 'Ingredient'
        db.delete_table('registrations_ingredient')

        # Deleting model 'Product'
        db.delete_table('registrations_product')

        # Deleting model 'MSHPrice'
        db.delete_table('registrations_mshprice')

        # Deleting model 'Manufacturer'
        db.delete_table('registrations_manufacturer')

        # Deleting model 'Site'
        db.delete_table('registrations_site')

        # Deleting model 'Supplier'
        db.delete_table('registrations_supplier')

        # Deleting model 'Pack'
        db.delete_table('registrations_pack')

        # Deleting model 'PackSize'
        db.delete_table('registrations_packsize')

        # Deleting model 'Registration'
        db.delete_table('registrations_registration')

        # Deleting model 'Procurement'
        db.delete_table('registrations_procurement')

        # Deleting model 'Context'
        db.delete_table('registrations_context')


    models = {
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
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '16'})
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
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Source']"}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'registrations.medicine': {
            'Meta': {'object_name': 'Medicine'},
            'dosageform': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.DosageForm']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ingredients': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['registrations.INN']", 'through': "orm['registrations.Ingredient']", 'symmetrical': 'False'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Source']"})
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
            'quantity': ('django.db.models.fields.IntegerField', [], {}),
            'registration': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Registration']"})
        },
        'registrations.procurement': {
            'Meta': {'object_name': 'Procurement'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Country']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incoterm': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Incoterm']"}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'pack': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.PackSize']", 'null': 'True', 'blank': 'True'}),
            'period': ('django.db.models.fields.IntegerField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Product']"}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Site']", 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Source']"}),
            'supplier': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Supplier']", 'null': 'True', 'blank': 'True'}),
            'validity': ('django.db.models.fields.DateField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'volume': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'registrations.product': {
            'Meta': {'object_name': 'Product'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'medicine': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Medicine']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Source']"})
        },
        'registrations.registration': {
            'Meta': {'object_name': 'Registration'},
            'application': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Country']"}),
            'expiry': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Site']", 'null': 'True', 'blank': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'packs': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['registrations.Pack']", 'through': "orm['registrations.PackSize']", 'symmetrical': 'False'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Product']"}),
            'registered': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Source']"}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'supplier': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Supplier']", 'null': 'True', 'blank': 'True'})
        },
        'registrations.site': {
            'Meta': {'object_name': 'Site'},
            'address': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'altemail': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'altphone': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'contact': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Country']", 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Manufacturer']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'prequalify': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Source']"}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'registrations.source': {
            'Meta': {'object_name': 'Source'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
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
            'prequalify': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registrations.Source']"}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['registrations']