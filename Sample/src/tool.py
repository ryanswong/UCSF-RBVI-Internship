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
        from chimerax.core.models import ADD_MODELS, REMOVE_MODELS
        t = session.triggers
        # self._add_handler = t.add_handler(ADD_MODELS, self._update_models)
        self._remove_handler = t.add_handler(REMOVE_MODELS, self._update_models)

        # Go!
        self._update_models()

    def _update_models(self, trigger=None, trigger_data=None):
        # Called to update page with current list of models
        import urllib.parse
        from chimerax.core.commands.cli import StructuresArg
        from urllib.parse import urlunparse, urlparse, quote, parse_qs, parse_qsl, urlencode
        from chimerax.core.atomic import AtomicStructure
        from urllib.parse import quote 

        if trigger_data is not None:

            for struct in self.structures:
                if struct in trigger_data:
                    self.structures.remove(struct)

        html = ['<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>',
                '<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.28.15/js/jquery.tablesorter.js"></script>',
                '<h2><font color= "#FF3399">ViewDockX</font></h2>',
                "<ul>"]

        html.append("""<style>
                        table, th, td {
                            border: 1px solid grey;
                            border-collapse: collapse;
                        }
                        </style>
                        
                        <table id="viewdockx_table" class="tablesorter" style="width:100%">""")
                # TRANSFERS ALL KEYS INTO A SET
        category_set = set()
        for struct in self.structures:
            try:
                category_set = {key for key in struct.viewdock_comment}
            except AttributeError:
                pass
        category_list = list(category_set)

        # ADDS ALL THE COLUMN HEADERS IN ALPHABETICAL ORDER

        # category_list = sorted(category_list)
        html.append('<thead><tr><th bgcolor= "#c266ff">ID</th>')



        #COLUMN HEADERS
        html.append('<th bgcolor="#00FFCC">NAME</th>') #just for NAME header

        for category in category_list:
            if category.upper() == "NAME":
                pass
            else: #all other headers
                html.append('<th style="font-family:arial;" bgcolor="#00FFCC">{}</th>'\
                    .format(category.upper()))
        html.append("</tr></thead><tbody>")
        #COLUMN DATA

        for struct in self.structures:
            try:
                comment_dict = struct.viewdock_comment
            except AttributeError:  #for files with empty comment sections
                comment_dict = {}
            html.append("<tr>")
            args = [("atomspec", struct.atomspec())]
            query = urlencode(args)
            url = urlunparse((self.CUSTOM_SCHEME, "", "", "", query, ""))


            html.extend(['<td style="font-family:arial;" bgcolor="#ebccff" align="center">',
                         """<input type="checkbox" class="checkbox" href="{}&checkbox=true"/>""".format(url),
                         '<a href="{}">model{}</a></td>'.format(url, struct.atomspec())])


            # ADDING VALUE FOR NAME
            for category in category_list:
                if category.upper() == "NAME":
                    try:
                        html.append('<td bgcolor = "#CCFFF5" align="center">{}</td>'\
                            .format(comment_dict[category]))
                    except KeyError:
                        html.append('<td align="center">missing</td>')

            #ADDING THE REST
            for category in category_list:
                try:
                    if category.upper() != "NAME":
                        html.append('<td bgcolor = "#CCFFF5" align="center">{}</td>'\
                            .format(comment_dict[category]))
                except KeyError:
                    html.append('<td style="font-family:arial;" align="center">missing</td>')
            html.append("</tr>")
        html.append("</tbody></table>")
        html.append("""<script>
                $(document).ready(function() 
                    { 
                        $("#viewdockx_table").tablesorter(); 
                    } 
                );
                </script>""")



        html.append("""<script>
                $(".checkbox").click(function(){

                if($(this).is(":checked")){
                    window.location=$(this).attr('href')
                }
                else{
                    // SOMETHING such as sset display to false
                }

                });
                </script>""")


        self.html_view.setHtml('\n'.join(html))

        print('\n'.join(html))






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
            # try:
            atomspec = query["atomspec"][0]
            # except (KeyError, ValueError):
            #     atomspec = "missing"
            # print("atomspec:", atomspec)
            # print("checkpoint 3")
            # structures, text, remainder = StructuresArg.parse(atomspec, self.session)
            structures, text, remainder = StructuresArg.parse(atomspec, self.session)
            self.session.ui.thread_safe(self._run, structures)

    def _run(self, structures):
        # ###Execute "sample count" command for given atomspec
        # from chimerax.core.commands import run
        for struct in self.structures:
            struct.display = struct in structures




        # run(self.session, "select " + text)
        # from chimerax.core.logger import StringPlainTextLog
        # with StringPlainTextLog(self.session.logger) as log:
        #     try:
        #     finally:
        #         html = "<pre>\n%s</pre>" % log.getvalue()
        #         js = ('document.getElementById("output").innerHTML = %s'
        #               % repr(html))
        #         self.html_view.page().runJavaScript(js)
