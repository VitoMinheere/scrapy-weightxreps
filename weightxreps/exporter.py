# -*- coding: utf-8 -*-

from .settings import EXPORT_FIELDS
from scrapy.exporters import CsvItemExporter

class CSVitemExporter(CsvItemExporter):

    def __init__(self, *args, **kwargs):
        kwargs['fields_to_export'] = EXPORT_FIELDS
        kwargs['encoding'] = 'utf-8'
        #settings.get('EXPORT_ENCODING', 'utf-8')
        super(CSVitemExporter, self).__init__(*args, **kwargs)
