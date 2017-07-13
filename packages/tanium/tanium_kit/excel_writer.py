from __future__ import absolute_import, division, print_function, unicode_literals

import csv
import logging
import re
import sys

LOG = logging.getLogger(__name__.split(".")[-1])

PY3 = sys.version_info[0] == 3
if PY3:
    string_types = str,  # noqa
    text_type = str  # noqa
    import io
    String_IO = io.StringIO
else:
    text_type = unicode  # noqa
    string_types = basestring,  # noqa
    import StringIO
    String_IO = StringIO.StringIO

# constants for line feeds
_LF = '\n'
_CR = '\r'
_CRLF = _CR + _LF


def fix_cr(v, cr):
    if isinstance(v, string_types):
        v = text_type(cr.join(v.splitlines()))
    return v


class ExcelWriterError(Exception):
    pass


class ExcelWriter(object):

    MSGS = []
    ROWS = []
    HEADERS = []
    CSV = ''

    def run(self, rows, **kwargs):
        if not isinstance(rows, (list, tuple)):
            err = "rows must be a list of dicts, you supplied: {}"
            err = err.format(type(rows).__name__)
            LOG.critical(err)
            raise ExcelWriterError(err)

        if not rows:
            err = "rows must be a list of dicts, you supplied an empty list"
            LOG.critical(err)
            raise ExcelWriterError(err)

        rows = self.process_rows(rows, **kwargs)
        headers = self.process_headers(rows, **kwargs)
        csv = self.create_csv(rows, headers, **kwargs)
        return csv

    def get_cr(self, **kwargs):
        valid = ['win', 'windows', 'nix', 'unix', 'mac', 'osx']
        cell_lines = kwargs.get('cell_lines', valid[0])

        if cell_lines and cell_lines.lower() not in valid:
            err = "invalid cell line value {!r}, must be one of: {}"
            err = err.format(cell_lines, ', '.join(valid))
            LOG.critical(err)
            raise ExcelWriterError(err)

        # join all cell values using windows Excel cell line endings (\r\n)
        if cell_lines.lower() == ['win', 'windows']:
            cr = _CRLF
        # join all cell values using unix line endings (\n)
        elif cell_lines.lower() == ['nix', 'unix']:
            cr = _LF
        # join all cell values using mac Excel cell line endings (\r)
        elif cell_lines.lower() in ['mac', 'osx']:
            cr = _CR
        else:
            cr = _CRLF
        return cell_lines, cr

    def process_rows(self, rows, **kwargs):
        cell_lines, cr = self.get_cr(**kwargs)
        # replace all newlines with cell_cr if cell_cr_win is not None
        if cell_lines:
            rows = [{fix_cr(k, cr): fix_cr(v, cr) for k, v in r.items()} for r in rows]
            m = "Forced cell line endings to {!r} for {} rows"
            m = m.format(cr, len(rows))
            LOG.debug(m)
        return rows

    def process_headers(self, rows, **kwargs):
        sort = kwargs.get('sort', True)
        headers = kwargs.get('headers', [])

        # get headers from dicts in rows if not supplied
        if not headers:
            headers = list(set([h for r in rows for h in r]))
            m = "gathered headers from {} rows: {!r}"
            m = m.format(len(rows), self.brief_l(headers))
            LOG.debug(m)

        # sort headers if sort is True
        if sort:
            headers = sorted(headers)
            m = "sorted headers using basic alpha sort: {!r}"
            m = m.format(self.brief_l(headers))
            LOG.debug(m)

        kwargs['headers'] = headers
        kwargs['headers'] = self.process_skips(**kwargs)
        kwargs['headers'] = self.process_firsts(**kwargs)
        kwargs['headers'] = self.process_lasts(**kwargs)
        result = kwargs['headers']
        return result

    def brief_l(self, l):
        result = ', '.join([x.splitlines()[0][0:10] for x in l])
        return result

    def process_skips(self, headers, **kwargs):
        skips = kwargs.get('skips', [])
        result = headers
        if skips:
            result = [h for h in headers if not any([re.match(r, h, re.I) for r in skips])]
            m = "Removed headers based on skips: {!r}, new headers: {!r}"
            m = m.format(', '.join(skips), self.brief_l(result))
            LOG.debug(m)
        return result

    def process_firsts(self, headers, **kwargs):
        firsts = kwargs.get('firsts', [])
        result = headers

        if firsts:
            f = []
            for r in firsts:
                f += [h for h in headers if re.match(r, h, re.I)]

            others = [h for h in headers if h not in f]
            result = f + others
            m = "firsts: {!r} changed header order to: {!r}"
            m = m.format(', '.join(firsts), self.brief_l(result))
            LOG.debug(m)
        return result

    def process_lasts(self, headers, **kwargs):
        lasts = kwargs.get('lasts', [])
        result = headers

        if lasts:
            l = []
            for r in lasts:
                l += [h for h in headers if re.match(r, h, re.I)]

            others = [h for h in headers if h not in l]
            result = others + l
            m = "lasts: {!r} changed header order to: {!r}"
            m = m.format(', '.join(lasts), self.brief_l(result))
            LOG.debug(m)
        return result

    def create_csv(self, rows, headers, **kwargs):
        ignore_missing = kwargs.get('ignore_missing', True)
        quote_all = kwargs.get('quote_all', True)

        if ignore_missing:
            action = 'ignore'
        else:
            action = 'raise'

        if quote_all is True:
            quoting = 'QUOTE_ALL'
        elif quote_all is False:
            quoting = 'QUOTE_NONNUMERIC'
        elif quote_all is None:
            quoting = 'QUOTE_NONE'

        m = "will {} errors if rows have headers that are not one of the {} headers"
        m = m.format(action, len(headers))
        LOG.debug(m)

        m = "quoting will {} for CSV output"
        m = m.format(quoting)
        LOG.debug(m)

        csvargs = {}
        csvargs['fieldnames'] = headers
        csvargs['extrasaction'] = action
        csvargs['quoting'] = getattr(csv, quoting)

        csv_io = String_IO()
        writer = csv.DictWriter(csv_io, **csvargs)
        writer.writeheader()
        writer.writerows(rows)
        csv_str = csv_io.getvalue()

        m = "generated {} bytes of csv text using csv.DictWriter()"
        m = m.format(len(csv_str))
        LOG.debug(m)
        return csv_str
