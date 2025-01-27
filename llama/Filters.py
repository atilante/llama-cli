from .operations import person_has_columns_value
from .common import count, read_json, write_json

class Filters:
  
  # PERSONS:
  #   Select INCLUSION
  #   THEN Store each Pseudo-User and whether all selected columns MATCH with value
  # INCLUSIONS:
  #   Select MATCHING sources OR all
  #   From THOSE Select MATCHING tables OR all
  #   From THOSE Select MATCHING columns OR all
  # EXCLUSIONS:
  #   Select NON-MATCHING sources
  #   From REST Select NON-MATCHING tables
  #   From REST Select NON-MATCHING columns

  PERSON_SELECT_JSON = 'person-select.json'

  def __init__(self, filters=None, inclusive=False):
    self.inclusive = inclusive
    self.person_filters = []
    self.inclusions = []
    self.exclusions = []
    self.add(filters or [])

  def add(self, filters):
    for f in filters:
      if 'source' in f or 'table' in f or 'column' in f:
        reverse = f.get('reverse', False)
        if not f.get('value') is None:
          self.person_filters.append(f)
        elif (not reverse if self.inclusive else reverse):
          self.inclusions.append(f)
        else:
          self.exclusions.append(f)
    return self

  def has_person_filters(self):
    return len(self.person_filters) > 0

  def person_filter_columns(self, sources):
    for f in self.person_filters:
      yield f, self._inclusion(f, sources)

  def person_select(self, sources, include_personal):
    persons = {}
    for f, sources in self.person_filter_columns(sources):
      for s in sources:
        for t in s['tables']:
          rows, _ = s['api'].fetch_rows(t, include_personal)
          for p, m in person_has_columns_value(rows, t['columns'], f['value'], not f['reverse']):
            persons[p] = persons.get(p, True) and m
    write_json(self.PERSON_SELECT_JSON, [{ 'person': p, 'included': m } for p, m in persons.items()])
    return [p for p, m in persons.items() if m]
  
  def filter(self, sources):
    out = sources
    for f in self.inclusions:
      out = self._inclusion(f, out)
    for f in self.exclusions:
      out = self._exclusion(f, out)
    return out

  @classmethod
  def _person_json(cls):
    return read_json(cls.PERSON_SELECT_JSON)

  @classmethod
  def person_status(cls):
    persons = cls._person_json()
    if persons:
      total = len(persons)
      included = count(p for p in persons if p['included'])
      return {
        'total': total,
        'included': included,
        'percent': round(100 * included / total),
      }
    return None

  @classmethod
  def person_included(cls):
    status = cls._person_json()
    return [p['person'] for p in status if p['included']] if status else None

  @classmethod
  def _inclusion(cls, filter, sources):
    sources_selected = []
    for s in sources:
      if cls._match_source(filter, s):
        tables_selected = []
        for t in s['tables']:
          if cls._match_table(filter, t):
            columns_selected = [c for c in t['columns'] if cls._match_column(filter, c)]
            columns_removed = [c for c in t['columns'] if not c in columns_selected]
            if not 'column' in filter or len(columns_selected) > 0:
              tables_selected.append({ **t, 'columns': columns_selected, 'columns_rm': columns_removed })
        if len(tables_selected) > 0:
          sources_selected.append({ **s, 'tables': tables_selected })
    return sources_selected

  @classmethod
  def _exclusion(cls, filter, sources):
    sources_selected = []
    for s in sources:
      if not cls._match_source(filter, s):
        sources_selected.append(s)
      else:
        tables_selected = []
        for t in s['tables']:
          if not cls._match_table(filter, t):
            tables_selected.append(t)
          else:
            columns_selected = [c for c in t['columns'] if not cls._match_column(filter, c)]
            columns_removed = [c for c in t['columns'] if not c in columns_selected]
            if len(columns_selected) > 0:
              tables_selected.append({ **t, 'columns': columns_selected, 'columns_rm': columns_removed })
        if len(tables_selected) > 0:
          sources_selected.append({ **s, 'tables': tables_selected })
    return sources_selected

  @staticmethod
  def _match_source(filter, source):
    m = filter.get('source')
    return m is None or m == source['id']

  @staticmethod
  def _match_table(filter, table):
    m = filter.get('table')
    by_id = filter.get('table_by_id', False)
    return (
      m is None
      or (by_id and m == str(table['id']))
      or (not by_id and m in table['name'])
    )

  @staticmethod
  def _match_column(filter, column):
    m = filter.get('column')
    return m is None or m in column['key']
