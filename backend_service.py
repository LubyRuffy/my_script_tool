# -*- coding: utf-8 -*-
# @Author: bunny
# @Date:   2016-02-26 11:03:05
# @Last Modified by:   bunny
# @Last Modified time: 2016-02-26 11:28:40
from sqlalchemy import create_engine
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, DateTime, Text, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from libnmap.plugins.backendplugin import NmapBackendPlugin
from libnmap.reportjson import ReportDecoder
from datetime import datetime
import json


Base = declarative_base()

class NmapSqlPlugin(NmapBackendPlugin):
    class Reports(Base):
        __tablename__ = 'assets_result'
        id = Column('id', Integer, primary_key=True)
        taskid = Column('taskid', String(256))
        inserted = Column('inserted', DateTime(), default='now')
        address = Column('address', String(256))
        port = Column('port', Integer)
        service = Column('service', String(256))
        state = Column('state', String(12))
        os = Column('os', String(256))
        protocol = Column('protocol', String(12))
        product = Column('product', String(64))
        # product_version = Column('product_version', String(64))
        # product_extrainfo = Column('product_extrainfo', String(128))
        banner = Column('banner', String(256))
        scripts_results = Column('scripts_results', Text)

        def __init__(self, obj_NmapReport):
            self.inserted = datetime.fromtimestamp(int(obj_NmapReport.endtime))
            self.taskid = obj_NmapReport.taskid
            self.address = obj_NmapReport.address
            self.port = obj_NmapReport.port
            self.service = obj_NmapReport.service
            self.state = obj_NmapReport.state
            self.protocol = str(obj_NmapReport.protocol)
            self.product = str(obj_NmapReport.product)
            # self.product_version = str(obj_NmapReport.product_version)
            # self.product_extrainfo = str(obj_NmapReport.product_extrainfo)
            self.banner = str(obj_NmapReport.banner)

            if len(obj_NmapReport.scripts_results) > 0:
                self.scripts_results = obj_NmapReport.scripts_results[0]['output']
            else:
                self.scripts_results = None

            if len(obj_NmapReport.os.osmatch()) > 0:
                self.os = obj_NmapReport.os.osmatch()[0]
            else:
                self.os = None

        def decode(self):
            json_decoded = self.report_json.decode('utf-8')
            nmap_report_obj = json.loads(json_decoded, cls=ReportDecoder)
            return nmap_report_obj

    def __init__(self, **kwargs):
        NmapBackendPlugin.__init__(self)
        self.engine = None
        self.url = None
        self.Session = sessionmaker()

        if 'url' not in kwargs:
            raise ValueError
        self.url = kwargs['url']
        del kwargs['url']
        try:
            self.engine = create_engine(self.url, **kwargs)
            Base.metadata.create_all(bind=self.engine, checkfirst=True)
            self.Session.configure(bind=self.engine)
        except:
            raise

    def insert(self, nmap_report):
        sess = self.Session()
        report = NmapSqlPlugin.Reports(nmap_report)
        sess.add(report)
        sess.commit()
        reportid = report.id
        sess.close()
        return reportid if reportid else None

    def get(self, report_id=None):
        if report_id is None:
            raise ValueError
        sess = self.Session()
        our_report = (
            sess.query(NmapSqlPlugin.Reports).filter_by(id=report_id).first())
        sess.close()
        return our_report.decode() if our_report else None

    def getall(self):
        sess = self.Session()
        nmapreportList = []
        for report in (
                sess.query(NmapSqlPlugin.Reports).
                order_by(NmapSqlPlugin.Reports.inserted)):
            nmapreportList.append((report.id, report.decode()))
        sess.close()
        return nmapreportList

    def delete(self, report_id=None):
        if report_id is None:
            raise ValueError
        nb_line = 0
        sess = self.Session()
        nb_line = sess.query(NmapSqlPlugin.Reports).\
            filter_by(id=report_id).delete()
        sess.commit()
        sess.close()
        return nb_line
