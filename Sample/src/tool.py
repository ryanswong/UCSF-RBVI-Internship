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

    def delete(self):
        t = self.session.triggers
        if self._remove_handler:
            t.remove_handler(self._remove_handler)
            self._remove_handler = None
        super().delete()

    def _update_models(self, trigger=None, trigger_data=None, checkbox=None):
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
            if not self.structures:
                self.delete()
                return

        html = ['<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>',
                '<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.28.15/js/jquery.tablesorter.js"></script>',
                '<h2><font color= "#FF8080">ViewDockX</font></h2>',
                "<ul>"]

        html.append("""<style>
                    table, th, td {
                    border: 1px solid grey;
                    border-collapse: collapse;}

                    th { background-color: #00FFCC; font-family:arial;}
                    td { background-color: #CCFFF5; text-align: center; font-family:arial;}
                    th.id { background-color: #c266ff; text-align: center;}
                    td.id {background-color: #ebccff; text-align: left;}
                    .checkbox {display: none; white-space: nowrap}

                    </style>""")



        # TRANSFERS ALL KEYS INTO A SET, THEN A LIST
        category_set = set()
        for struct in self.structures:
            try:
                category_set = {key for key in struct.viewdock_comment}
            except AttributeError:
                pass
        category_list = sorted(list(category_set))

        html.append('<input type="checkbox" id="show_checkboxes"/>show checkboxes</>')
        html.append('<span class="checkbox"><input type="checkbox" id="check_all" />check all</></span>')



        ####################
        ####    TABLE   ####
        ####################

        html.append('<table id="viewdockx_table" class="tablesorter" style="width:100%">')
        
        ###########################
        ###    COLUMN HEADERS   ###
        ###########################

        #   COLUMN HEADER    | ID |
        html.append('<thead><tr>')
        html.append('<th class="id">ID</th>')

        #   COLUMN HEADERS    | NAME |...|...|...
        html.append('<th>NAME</th>') 
        for category in category_list:
            if category.upper() == "NAME":
                pass
            else:
                html.append('<th>{}</th>'\
                    .format(category.upper()))
        html.append("</tr></thead>")

        ########################
        ###    COLUMN DATA   ###
        ########################
        html.append('<tbody>')
        for struct in self.structures:
            try:
                comment_dict = struct.viewdock_comment
            except AttributeError:  #for files with empty comment sections
                comment_dict = {}

            # MAKES THE URL FOR EACH STRUCTURE
            args = [("atomspec", struct.atomspec())]
            query = urlencode(args)
            url = urlunparse((self.CUSTOM_SCHEME, "", "", "", query, ""))

            # ADDING ID VALUE
            html.append("<tr>")
            html.extend(['<td class="id">',
                         # for checkbox + atomspec string
                         '<span style="display:none; white-space: nowrap" class="checkbox">\
                         <input class="checkbox, struct" type="checkbox" href="{}"/>\
                         {}</span>'.format(url, struct.atomspec()[1:]),

                         # for atomspec links only
                         '<span class="link"><a href="{}">{}</a></span>'.format(url,
                            struct.atomspec()[1:]),
                         '</td>']),

            # ADDING VALUE FOR NAME
            for category in category_list:
                if category.upper() == "NAME":
                    try:
                        html.append('<td>{}</td>'.format(comment_dict[category]))
                    except KeyError:
                        html.append('<td>missing</td>')

            # ADDING THE REST
            for category in category_list:
                try:
                    if category.upper() != "NAME":
                        html.append('<td>{}</td>'\
                            .format(comment_dict[category]))
                except KeyError:
                    html.append('<td>missing</td>')
            html.append("</tr>")
        html.append("</tbody>")
        html.append("</table>")




        html.append("""
            <script>
            $(document).ready(function() 
                { 
                    $("#viewdockx_table").tablesorter(); 
                } 
            );

            $("#show_checkboxes").click(function(){

                if($(this).is(":checked")){
                    $(".checkbox").show();
                    $(".link").hide();
                }
                else{
                    $(".checkbox").hide();
                    $(".link").show();
                }

                });
            </script>

            <script>
            $(".struct").click(function(){

            if($(this).is(":checked")){
                window.location=$(this).attr('href')+"&display=1";
            }
            else{
                window.location=$(this).attr('href')+"&display=0";
            }

            });
            </script>

            <script>
            $("#check_all").click(function(){

            if($(this).is(":checked")){
                $(".struct").prop('checked', true);
                window.location="viewdockx:?show_all=true";
            }
            else{
                $(".struct").prop('checked', false);
                window.location="viewdockx:?show_all=false";
            }
            });
            </script>

            <script>
            $("#viewdockx_table tr td").click(function() {
                //Reset
                $("#viewdockx_table td, th").removeClass("highlight");
                //Add highlight class to new column
                var index = $(this).index();
                $("#viewdockx_table tr").each(function(i, tr) {
                    $(tr).find('td, th').eq(index).addClass("highlight");
                });
                alert($(`#viewdockx_table td:nth-child(${index + 1}`).map(function(){
                    return $(this).text();
                }).get());
            });
            </script>

            <style>

            .highlight {
              background-color: yellow;
            }   
            </style>""")

        # import os
        # file = os.path.join(os.getcwd(), "viewdockx_frame.html")
        # # print("printing path", os.path)
        # print(file)
        # print(os.path.dirname(os.path.abspath(__file__)))
        # print(os.path.join(os.path.dirname(os.path(__file__)), "viewdockx_frame.html"))
        # with open(file, "r") as f:
        #     template = f


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

            print("query:", query)

            if "show_all" in query.keys():
                show_all = query["show_all"][0]
                self.session.ui.thread_safe(self._checkall, show_all)
            # elif "show_checkboxes" in query.keys():
            #     if query["show_checkboxes"][0] == "true":
            #         self.session.ui.thread_safe(self._update_models, checkbox=True)
            #     else:
            #         self.session.ui.thread_safe(self._update_models, checkbox=False)
                    
                # structures, text, remainder = StructuresArg.parse(atomspec, self.session)
            else:
                # try:
                atomspec = query["atomspec"][0]
                disp = query["display"][0]
                # except (KeyError, ValueError):
                #     atomspec = "missing"
                # print("atomspec:", atomspec)
                # print("checkpoint 3")
                # structures, text, remainder = StructuresArg.parse(atomspec, self.session)
                structures, text, remainder = StructuresArg.parse(atomspec, self.session)
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
