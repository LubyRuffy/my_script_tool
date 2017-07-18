# report-ng
# Copyright (c) 2014-2015 Marcin Woloszyn (@hvqzao)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


from util import UnsortableOrderedDict
import zlib
import base64
from lxml import etree
from lxml.html import soupparser
import re
import mangle


def fine_tune(content, fullurl):
    if filter(lambda x: x == content[:len(x)], ['<html>', '<ihtml>']):
        content = re.sub('<br\/>(<br\/>)+', '<br/>', content)
        content = re.sub('(\s|\t|\n)+', ' ', content)
        content = re.sub('\s?<br\/>\s?', '<br/>', content)
        content = re.sub('<\/?drc_[^>]+>', '', content)
        content = re.sub('<\/?hp-img[^>]*>', '', content)
        content = re.sub('^<html>(<br\/>|\s)+', '<html>', content)
        content = re.sub('(<br\/>|\s)+<\/html>', '</html>', content)
        content = re.sub('<\/ol><br\/>', '</ol>', content)
        #content = re.sub('><br\/>', '>', content)
        #content = re.sub('<br\/><', '<', content)
        content = re.sub('<\/li><br\/><li>', '</li><li>', content)
    content = re.sub('(?i)~FullURL~', fullurl, content)
    content = content.strip()
    #print content
    #print
    return content
    
def webinspect_import(xml, requests_and_responses=False):
    # initially, HP WebInspect (10.1.177.0), recently 10.40
    issues_list = []
    issues = xml.xpath('/Sessions/Session/Issues/Issue')
    for issue in issues:
        session = issue.getparent().getparent()
        scheme = session.xpath('./Scheme')[0].text
        host = session.xpath('./Host')[0].text
        port = int(session.xpath('./Port')[0].text)
        # remove port if not needed
        if scheme.lower() == 'http' and port == 80:
            port = ''
        if scheme.lower() == 'https' and port == 443:
            port = ''
        #print scheme, host, port
        request = session.xpath('./RawRequest')[0].text
        response = session.xpath('./RawResponse')[0].text
        method = session.xpath('./Request/Method')[0].text
        response_element = session.xpath('./Response')
        if response_element:
            status_code = int(response_element[0].xpath('./StatusCode')[0].text)
            status_description = response_element[0].xpath('./StatusDescription')[0].text
        else:
            status_code, status_description = (None, None)
        #print status_code, status_description
        location = ' '.join(request.split('\n')[0].split(' ')[1:-1])
        fullurl = scheme+'://'+host+['', ':'+str(port)][bool(port)]+location
        #print method, location
        if method == 'POST':
            # fix tested only for Burp reports:
            #post = request.split('\n')[-1]
            request_temp = request.replace('\r','')
            loc = request_temp.find('\n\n')
            if loc != -1:
                post = request_temp[loc:].strip()
            del request_temp
        else:
            post = ''
        vulnparam = session.xpath('./AttackParamDescriptor')[0].text
        if vulnparam == None:
            vulnparam = ''
        severity_id = int(issue.xpath('./Severity')[0].text)
        severity = ['Informational', 'Low', 'Medium', 'High', 'Critical'][severity_id]
        name = issue.xpath('./Name')[0].text
        if issue.xpath('./CheckTypeID')[0].text == 'Best Practices':
            severity = 'Best Practices'
        vuln_id = issue.xpath('./VulnerabilityID')[0].text
        #print severity,'\t',name
        classifications = map(lambda x: [x.attrib['kind'], x.attrib['identifier'], x.attrib['href'], x.text],
                              issue.xpath('./Classifications/Classification'))
        report_sections = map(lambda x: [x.xpath('./Name')[0].text, x.xpath('./SectionText')[0].text],
                              issue.xpath('./ReportSection'))
        for i in range(len(report_sections)):
            if report_sections[i][1]:
                report_sections[i][1] = fine_tune(etree.tostring(soupparser.fromstring(report_sections[i][1])), fullurl)
        #print issue.xpath ('./DetectionSelection/*')
        issues_item = [
            ['Severity', severity],
            ['severity_id', severity_id],
            ['Name', name],
            ['vuln_id', vuln_id],
            ['Scheme', scheme],
            ['Host', host],
            ['Port', port],
            ['Method', method],
            ['Location', location],
            ['Post', post],
            ['VulnParam', vulnparam],
            ['Example', UnsortableOrderedDict([('VulnParam',vulnparam,),('Request',mangle.request_tune(request),),('Response',mangle.response_tune(response),)])],
            #['Request', request],
        ]
        if requests_and_responses:
            issues_item += [
                ['Request', base64.b64encode (zlib.compress (request.encode('utf-8')))],
                ['Response', base64.b64encode (zlib.compress (response.encode('utf-8')))],
            ]
        issues_item += [
            ['StatusCode', status_code],
            ['StatusDescription', status_description],
            ['Classifications', map(lambda x: UnsortableOrderedDict([['Name', x[3]], ['URL', '<ihtml><a href="'+x[2]+'">'+x[2]+'</a></ihtml>']]), classifications)],
            ['ReportSections', UnsortableOrderedDict(map(lambda x: [x[0].replace(' ', ''), x[1]], report_sections))],
        ]
        issues_list += [UnsortableOrderedDict(issues_item)]
    findings = []
    for vuln_id in sorted(set(map(lambda x: str(x['vuln_id']), issues_list))):
        issue = UnsortableOrderedDict()
        for i in filter(lambda x: str(x['vuln_id']) == vuln_id, issues_list):
            for j in ['Name', 'Severity', 'severity_id', 'ReportSections', 'Classifications', 'Example']:
                if j not in issue:
                    issue[j] = i[j]
                    #else:
                    #    if issue[j] != i[j]:
                    #        print j
            for j in ['Occurrences']:
                if j not in issue:
                    issue[j] = []
                v = UnsortableOrderedDict()
                for k in ['Scheme', 'Host', 'Port', 'Method', 'Location', 'Post', 'VulnParam', 'StatusCode', 'StatusDescription']:
                    v[k] = i[k]
                if requests_and_responses:
                    for k in ['Request','Response']:
                        v[k] = i[k]                        
                issue[j] += [v]
        findings += [issue]
    findings.sort(key=lambda x: x['severity_id'], reverse=True)
    for i in findings:
        del i['severity_id']
    return UnsortableOrderedDict([['Findings', findings], ])

if __name__ == '__main__':
    pass

    import yaml
    from lxml import etree
    xml = etree.parse('./')
    scan = webinspect_import(xml)
    sample = scan['Findings'][-2]
    print yaml.dump(sample, default_flow_style=False, allow_unicode=True).decode('utf-8')
