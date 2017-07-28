# vim: set expandtab shiftwidth=4 softtabstop=4:
from chimerax.core.atomic import AtomicStructure
from chimerax.core.tools import ToolInstance


class ViewDockTool(ToolInstance):

    SESSION_ENDURING = False
    SESSION_SKIP = True         # No session saving for now
    CUSTOM_SCHEME = "viewdockx"    # HTML scheme for custom links
    display_name = "ViewDockX"

    def __init__(self, session, tool_name, structures=None):
        # Standard template stuff for intializing tool
        super().__init__(session, tool_name)
        from chimerax.core.ui.gui import MainToolWindow
        self.tool_window = MainToolWindow(self)
        self.tool_window.manage(placement="side")
        if structures is None:
            structures = session.models.list(type=AtomicStructure)
        self.structures = structures
        parent = self.tool_window.ui_area

        # Create an HTML viewer for our user interface.
        # We can include other Qt widgets if we want to.
        from PyQt5.QtWidgets import QGridLayout
        from chimerax.core.ui.widgets import HtmlView
        layout = QGridLayout()
        self.html_view = HtmlView(parent, size_hint=(575, 200),
                                  interceptor=self._navigate,
                                  schemes=[self.CUSTOM_SCHEME])
        layout.addWidget(self.html_view, 0, 0)  # row 0, column 0
        parent.setLayout(layout)

        # Register for model addition/removal so we can update model list
        from chimerax.core.models import REMOVE_MODELS
        t = session.triggers
        # self._add_handler = t.add_handler(ADD_MODELS, self._update_models)
        self._remove_handler = t.add_handler(
            REMOVE_MODELS, self._update_models)

        # Go!
        self._update_models()

    def delete(self):
        t = self.session.triggers
        if self._remove_handler:
            t.remove_handler(self._remove_handler)
            self._remove_handler = None
        super().delete()

    def _update_models(self, trigger=None, trigger_data=None):
        # Called to update page with current list of models
        from urllib.parse import urlunparse, urlparse, quote, parse_qs, parse_qsl, urlencode
        # from chimerax.core.atomic import AtomicStructure

        if trigger_data is not None:

            for struct in self.structures:
                if struct in trigger_data:
                    self.structures.remove(struct)
            if not self.structures:
                self.delete()
                return

        # TRANSFERS ALL KEYS INTO A SET, THEN A LIST
        category_set = set()
        for struct in self.structures:
            try:
                category_set = {key for key in struct.viewdock_comment}
            except AttributeError:
                pass
        category_list = sorted(list(category_set))

        ####################
        ####    TABLE   ####
        ####################

        table = (
            ['<table id="viewdockx_table" class="tablesorter" style="width:100%">'])

        ###########################
        ###    COLUMN HEADERS   ###
        ###########################

        #   COLUMN HEADER    | ID |
        table.append('<thead><tr>')
        table.append('<th class="id">ID</th>')

        #   COLUMN HEADERS    | NAME |...|...|...
        table.append('<th>NAME</th>')
        for category in category_list:
            if category.upper() == "NAME":
                pass
            else:
                table.append('<th>{}</th>'.format(category.upper()))
        table.append("</tr></thead>")

        ########################
        ###    COLUMN DATA   ###
        ########################
        table.append('<tbody>')
        for struct in self.structures:
            try:
                comment_dict = struct.viewdock_comment
            except AttributeError:  # for files with empty comment sections
                comment_dict = {}

            # MAKES THE URL FOR EACH STRUCTURE
            args = [("atomspec", struct.atomspec())]
            query = urlencode(args)
            url = urlunparse((self.CUSTOM_SCHEME, "", "", "", query, ""))

            # ADDING ID VALUE
            table.append("<tr>")
            table.extend(['<td class="id">',
                          # for checkbox + atomspec string
                          '<span class="checkbox">'
                          '<input class="checkbox, struct" type="checkbox" href="{}"/>'
                          '{}</span>'.format(url, struct.atomspec()[1:]),

                          # for atomspec links only
                          '<span class="link"><a href="{}">{}</a></span>'
                          .format(url, struct.atomspec()[1:]),
                          '</td>'])

            # ADDING VALUE FOR NAME
            for category in category_list:
                if category.upper() == "NAME":
                    try:
                        table.append(
                            '<td>{}</td>'.format(comment_dict[category]))
                    except KeyError:
                        table.append('<td>missing</td>')

            # ADDING THE REST
            for category in category_list:
                try:
                    if category.upper() != "NAME":
                        table.append('<td>{}</td>'
                                     .format(comment_dict[category]))
                except KeyError:
                    table.append('<td>missing</td>')
            table.append("</tr>")
        table.append("</tbody>")
        table.append("</table>")

        import os
        from PyQt5.QtCore import QUrl

        # os.path.join()

        dir_path = os.path.dirname(os.path.abspath(__file__))
        lib_path = os.path.join(dir_path, "lib")

        qurl = QUrl.fromLocalFile(os.path.join(dir_path, "viewdockx.html"))

        with open(os.path.join(dir_path, "viewdockx_frame.html"), "r") as file:
            template = file.read()
        output = template.replace("TABLE", ('\n'.join(table)))\
                         .replace("urlbase", qurl.url())
        self.html_view.setHtml(output, qurl)

        output_file = os.path.join(
            "C:/Users/Ryan/Documents/GitHub/UCSF-RBVI-Internship/ViewDockX/src/output-test.html")
        print(output_file)
        with open(output_file, "w") as file2:
            file2.write(output)
        print("TEST SUCCESS")

    def _navigate(self, info):
        # Called when link is clicked.
        # "info" is an instance of QWebEngineUrlRequestInfo
        from chimerax.core.commands.cli import StructuresArg
        from urllib.parse import parse_qs
        url = info.requestUrl()
        scheme = url.scheme()
        if scheme == self.CUSTOM_SCHEME:
            # Intercept our custom scheme.
            # Method may be invoked in a different thread than
            # the main thread where Qt calls may be made.

            query = parse_qs(url.query())
            if "show_all" in query.keys():
                show_all = query["show_all"][0]
                self.session.ui.thread_safe(self._checkall, show_all)
            else:
                try:
                    atomspec = query["atomspec"][0]
                    disp = query["display"][0]
                except (KeyError, ValueError):
                    atomspec = "missing"
                # print("atomspec:", atomspec)
                # print("checkpoint 3")
                structures, text, remainder = StructuresArg.parse(
                    atomspec, self.session)
                self.session.ui.thread_safe(self._run, structures, disp)

    def _run(self, structures, disp):
        # ###Execute "sample count" command for given atomspec
        # from chimerax.core.commands import run

        # for struct in self.structures:
        #     struct.display = struct in structures

        if disp == "0":
            for struct in self.structures:
                if structures[0] == struct:
                    struct.display = False
        # elif disp == "2":
        #     for struct in self.structures:
        #         struct.display = struct in structures
        else:
            for struct in self.structures:
                if structures[0] == struct:
                    struct.display = True

    def _checkall(self, show_all):

        if show_all == "true":
            for struct in self.structures:
                struct.display = True

        else:
            for struct in self.structures:
                struct.display = False

        # run(self.session, "select " + text)
        # from chimerax.core.logger import StringPlainTextLog
        # with StringPlainTextLog(self.session.logger) as log:
        #     try:
        #     finally:
        #         html = "<pre>\n%s</pre>" % log.getvalue()
        #         js = ('document.getElementById("output").innerHTML = %s'
        #               % repr(html))
        #         self.html_view.page().runJavaScript(js)


# ## TEST PURPOSE ONLY ####

# def test_run(file_name):
#     import os
#     file = os.path.join(os.getcwd(), 'example_files/{}'.format(file_name))
#     with open(file, "r") as stream:
#         open_mol2(None, stream, file)

# test_run("ras.mol2")
# l2")
