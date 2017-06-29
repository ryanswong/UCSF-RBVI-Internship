# vim: set expandtab shiftwidth=4 softtabstop=4:

from chimerax.core.tools import ToolInstance


class ViewDockTool(ToolInstance):

    SESSION_ENDURING = False
    SESSION_SKIP = True         # No session saving for now
    CUSTOM_SCHEME = "viewdockx"    # HTML scheme for custom links
    display_name = "ViewDockX"

    def __init__(self, session, tool_name, structures = None):
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
        from chimerax.core.models import ADD_MODELS, REMOVE_MODELS
        t = session.triggers
        self._add_handler = t.add_handler(ADD_MODELS, self._update_models)
        self._remove_handler = t.add_handler(REMOVE_MODELS, self._update_models)

        # Go!
        self._update_models()

    def _update_models(self, trigger=None, trigger_data=None):
        # Called to update page with current list of models
        from chimerax.core.atomic import AtomicStructure
        html = ['<script type="text/javascript" src="/path/to/jquery-latest.js"></script>', 
        '<script type="text/javascript" src="/path/to/jquery.tablesorter.js"></script>', '<h2><font color= "#FF3399">ViewDockX</font></h2>', "<ul>"]
        from urllib.parse import quote


        html.append("""<style>
                        table, th, td {
                            border: 1px solid black;
                            border-collapse: collapse;
                        }
                        </style>
                        
                        <table style="width:100%">""")

        # TRANSFERS ALL KEYS INTO A SET
        s = set()
        for struct in self.structures:
            for key in struct.viewdock_comment:
                s.add(key)

        # ADDS ALL THE COLUMN HEADERS IN ALPHABETICAL ORDER
        # s = sorted(s)
        html.append('<tr><th bgcolor= "#c266ff">ID</th>')

        #COLUMN HEADERS
        html.append('<th bgcolor="#00FFCC">NAME</th>')
        for category in s:
            if category.upper() == "NAME":
                pass
            else:
                html.append('<th bgcolor="#00FFCC">{}</th>'.format(category.upper()))
        html.append("</tr>")

        for struct in self.structures:
            comment_dict = struct.viewdock_comment
            html.append("<tr>")
            html.append('<td  bgcolor="#ebccff" align="center"><a href=\"%s:%s\">%s - %s</a></td>' %
                        (self.CUSTOM_SCHEME, quote(struct.atomspec()),  # "viewdock:#1.1"
                         struct.id_string(), struct.name))
            for category in s:
                if category.upper() == "NAME":
                    html.append('<td bgcolor = "#CCFFF5" align="center">{}</td>'.format(comment_dict[category]))
            for category in s:
                try:
                    if category.upper() == "NAME":
                        pass
                    else:
                        html.append('<td bgcolor = "#CCFFF5" align="center">{}</td>'.format(comment_dict[category]))
                except KeyError:
                    html.append('<td align="center">missing</td>')
            html.append("</tr>")


        html.append("""</table>""")


        self.html_view.setHtml('\n'.join(html))

    def _navigate(self, info):
        # Called when link is clicked.
        # "info" is an instance of QWebEngineUrlRequestInfo
        url = info.requestUrl()
        scheme = url.scheme()
        if scheme == self.CUSTOM_SCHEME:
            # Intercept our custom scheme.
            # Method may be invoked in a different thread than
            # the main thread where Qt calls may be made.
            self.session.ui.thread_safe(self._run, url.path())

    def _run(self, atomspec):
        # Execute "sample count" command for given atomspec
        from chimerax.core.commands import run
        run(self.session, "select " + atomspec)
        # from chimerax.core.logger import StringPlainTextLog
        # with StringPlainTextLog(self.session.logger) as log:
        #     try:
        #     finally:
        #         html = "<pre>\n%s</pre>" % log.getvalue()
        #         js = ('document.getElementById("output").innerHTML = %s'
        #               % repr(html))
        #         self.html_view.page().runJavaScript(js)
