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
        '<script type="text/javascript" src="/path/to/jquery.tablesorter.js"></script>', "<h2>ViewDockX</h2>", "<ul>"]
        from urllib.parse import quote
        for m in self.structures:

            print("test", m.viewdock_comment["Number"])
            html.append("<li><a href=\"%s:%s\">%s - %s</a></li>" %
                        (self.CUSTOM_SCHEME, quote(m.atomspec()), #"viewodck:#1.1"
                         m.id_string(), m.name))

        # html.extend(["</ul>",
        #              "<h3>Output : </h3>",

        #              '<div id="output">Counts appear here</div>'])
        self.html_view.setHtml('\n'.join(html))
        html.append("""<style>
table, th, td {
    border: 1px solid black;
    border-collapse: collapse;
}
</style>

<table style="width:100%">
  <tr>
    <th>Structure</th>
    <th>Number</th>
    <th>Source num</th> 
    <th>Name</th>
    <th>Description</th>
    <th>Reflect</th>
    <th>Energy Score</th>
    <th>IM Van der waals</th>
    <th>IM electrostatic</th>
    <th>RMSD</th>
  </tr>
  <tr>""")


        for struct in self.structures:
            comment = struct.viewdock_comment
            html.append("""  <tr>
    <td>{}</td>
    <td>{}</td>
    <td>{}</td>
    <td>{}</td>
    <td>{}</td>
    <td>{}</td>
    <td>{}</td>
    <td>{}</td>
    <td>{}</td>
  </tr>""".format(comment["Number"], comment["Source num"], comment["Name"], comment["Description"], comment["Name"],\
    comment["Energy score"], comment["intermolecular van der Waals"] , comment["intermolecular electrostatic"], comment["RMSD from input orientation (A)"]))

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
