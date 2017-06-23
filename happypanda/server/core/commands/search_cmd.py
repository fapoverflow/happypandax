from happypanda.common import hlogger, exceptions, utils
from happypanda.server.core.command import Command, CommandEvent, CommandEntry
from happypanda.server.core.commands import database_cmd
from happypanda.server.core import db


log = hlogger.Logger(__name__)


class ParseSearchFilter(Command):
    """
    Parse a search filter

    Dividies term into ns:tag pieces, returns a tuple of ns:tag pieces
    """

    parse = CommandEntry("parse", tuple, str)
    parsed = CommandEvent("parsed", tuple)

    def __init__(self):
        super().__init__()
        self.filter = ''
        self.pieces = tuple()

    @parse.default()
    def _get_terms(term):

        # some variables we will use
        pieces = []
        piece = ''
        qoute_level = 0
        bracket_level = 0
        brackets_tags = {}
        current_bracket_ns = ''
        end_of_bracket = False
        blacklist = ['[', ']', '"', ',']

        for n, x in enumerate(term):
            # if we meet brackets
            if x == '[':
                bracket_level += 1
                brackets_tags[piece] = set()  # we want unique tags!
                current_bracket_ns = piece
            elif x == ']':
                bracket_level -= 1
                end_of_bracket = True

            # if we meet a double qoute
            if x == '"':
                if qoute_level > 0:
                    qoute_level -= 1
                else:
                    qoute_level += 1

            # if we meet a whitespace, comma or end of term and are not in a
            # double qoute
            if (x == ' ' or x == ',' or n == len(
                    term) - 1) and qoute_level == 0:
                # if end of term and x is allowed
                if (n == len(term) - 1) and x not in blacklist and x != ' ':
                    piece += x
                if piece:
                    if bracket_level > 0 or end_of_bracket:  # if we are inside a bracket we put piece in the set
                        end_of_bracket = False
                        if piece.startswith(current_bracket_ns):
                            piece = piece[len(current_bracket_ns):]
                        if piece:
                            try:
                                brackets_tags[current_bracket_ns].add(piece)
                            except KeyError:  # keyerror when there is a closing bracket without a starting bracket
                                pass
                    else:
                        pieces.append(piece)  # else put it in the normal list
                piece = ''
                continue

            # else append to the buffers
            if x not in blacklist:
                if qoute_level > 0:  # we want to include everything if in double qoute
                    piece += x
                elif x != ' ':
                    piece += x

        # now for the bracket tags
        for ns in brackets_tags:
            for tag in brackets_tags[ns]:
                ns_tag = ns
                # if they want to exlucde this tag
                if tag[0] == '-':
                    if ns_tag[0] != '-':
                        ns_tag = '-' + ns
                    tag = tag[1:]  # remove the '-'

                # put them together
                ns_tag += tag

                # done
                pieces.append(ns_tag)

        return tuple(pieces)

    def main(self, search_filter: str) -> tuple:

        self.filter = search_filter

        pieces = set()

        with self.parse.call(search_filter) as plg:
            for p in plg.all(default=True):
                for x in p:
                    pieces.add(x)
        self.pieces = tuple(pieces)

        self.parsed.emit(self.pieces)

        return self.pieces


class PartialFilter(Command):
    """
    Perform a partial search on database model with a single term

    Accepts any term

    By default, the following models are supported:

    - User
    - NamespaceTags
    - Tag
    - Namespace
    - Artist
    - Circle
    - Status
    - Grouping
    - Language
    - Category
    - Collection
    - Gallery
    - Title
    - GalleryUrl

    Returns a set with ids of matched model items
    """

    models = CommandEntry("models", tuple)

    match_model = CommandEntry("match_model", set, db.Base, str)
    matched = CommandEvent("matched", set)

    def __init__(self):
        super().__init__()
        self.model = None
        self.term = ''
        self._supported_models = set()
        self.matched_ids = set()

    @models.default()
    def _models():
        return (
            db.NamespaceTags,
            db.Tag,
            db.Namespace,
            db.Artist,
            db.Circle,
            db.Status,
            db.Grouping,
            db.Language,
            db.Category,
            db.Collection,
            db.Gallery,
            db.Title,
            db.GalleryUrl
            )

    @match_model.default(capture=True)
    def _match_gallery(model, term, capture=db.Gallery):
        return set()

    @match_model.default(capture=True)
    def _match_models(model, term, capture=_models()):
        return set()

    def main(self, model: db.Base, term: str) -> set:

        self.model = model
        self.term = term

        with self.models.call() as plg:
            for p in plg.all(default=True):
                self._supported_models.update(p)

        if not self.model in self._supported_models:
            raise exceptions.CoreError(utils.this_command(self), "Model '{}' is not supported".format(model))

        with self.match_model.call_capture(self.model, self.model, self.term) as plg:
            for i in plg.all():
                self.matched_ids.update(i)

        self.matched.emit(self.matched_ids)

        return self.matched_ids

class OperatorFilter(PartialFilter):
    """
    Perform a partial search on database model with a single term

    Accepts a term with a namespace and by default one of the following operators included:
    - '>'
    - '<'

    Returns None if term is not accepted else a set with ids of matched model items
    """

    operators = CommandEntry("operators", tuple)
    accept = CommandEntry("accept", None)
    match = CommandEntry("match", None)

    def __init__(self):
        super().__init__()
        self._ops = set()

    @operators.default()
    def _operators():
        return ('>', '<')

    def main(self, model: db.Base, term: str) -> set:
        return None
        self.model = model
        self.term = term

        with self.operators.call() as plg:
            for o in plg.all(default=True):
                for x in o:
                    if isinstance(x, str):
                        self._ops.add(x)


class ModelFilter(Command):
    """
    Perform a full search on database model
    Returns a set of ids of matched model items
    """

    separate = CommandEntry("separate", tuple, tuple)
    include = CommandEntry("include", set, set)
    exclude = CommandEntry("exclude", set, set)

    included = CommandEvent("included", str, set)
    excluded = CommandEvent("excluded", str, set)
    matched = CommandEvent("matched", str, set)

    def __init__(self):
        super().__init__()
        self._model = None
        self.parsesearchfilter = None
        self.included_ids = set()
        self.excluded_ids = set()
        self.matched_ids = set()

    @separate.default()
    def _separate(pecies):

        include = []
        exclude = []

        for p in pecies:
            if p.startswith('-'):
                exclude.append(p[1:])  # remove '-' at the start
            else:
                include.append(p)

        return tuple(include), tuple(exclude)

    @classmethod
    def _match(model_name, pieces):
        ""
        model = database_cmd.GetModel().run(model_name)
        operatorfilter = OperatorFilter()
        partialfilter = PartialFilter()
        matched = set()

        for p in pieces:

            m = operatorfilter.main(model, p)
            if m is None:
                m = partialfilter.main(model, p)
            matched.update(m)

        return matched

    @include.default()
    def _include(model_name, pieces):
        return ModelFilter._match(model_name, pieces)

    @exclude.default()
    def _exclude(model_name, pieces):
        return ModelFilter._match(model_name, pieces)

    def main(self, model: db.Base, search_filter: str) -> set:
        assert isinstance(model, db.Base)

        self._model = model
        model_name = self._model.__name__

        self.parsesearchfilter = ParseSearchFilter()

        pieces = self.parsesearchfilter.run(search_filter)

        include = set()
        exclude = set()

        with self.separate.call(pieces) as plg:

            for p in plg.all():
                if len(p) == 2:
                    include.update(p[0])
                    exclude.update(p[1])

        with self.include.call(model_name, include) as plg:

            for i in plg.all():
                self.included_ids.update(i)

        self.included.emit(model_name, self.included_ids)

        with self.exclude.call(model_name, exclude) as plg:

            for i in plg.all():
                self.excluded_ids.update(i)

        self.excluded.emit(self._model.__name__, self.excluded_ids)

        self.matched_ids = self.included_ids
        self.matched_ids.difference_update(self.excluded_ids)

        self.matched.emit(self._model.__name__, self.matched_ids)

        return self.matched_ids