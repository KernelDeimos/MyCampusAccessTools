
class PageLoader:
    def __init__(self,url_base,url_action,semester,year,subj):
        self.actionURL = url_base + url_action

        self.set_term(semester,year)
        self.set_subj(subj)
        
    def set_term(self,semester,year):
        self.term_in = str(year) + str(acros.semester[semester])
    def set_subj(self,subj):
        self.subj = subj

    def get_page(self,(url,data)):
        req = urllib2.Request(url, data=data)
        """
        print("=== Headers ===")
        print(req.headers)
        print("=== Data ===")
        print(req.data)
        """
        response = urllib2.urlopen(req)
        pageContents = response.read()

        try:
            with open('./last_source.html','w') as f:
                f.write(pageContents)
        except IOError:
            print("Warning: PageLoader couldn't write to ./last_source.html")

        return pageContents
    def gen_url_and_data(self):
        url = self.actionURL

        term_in = self.term_in
        subj = self.subj

        vals = PostData()
        vals.add_item('TRM'                , "U")
        vals.add_item('term_in'            , term_in)        # OVER HERE
        vals.add_item('sel_subj'        , "dummy")
        vals.add_item('sel_day'            , "dummy")
        vals.add_item('sel_schd'        , "dummy")
        vals.add_item('sel_insm'        , "dummy")
        vals.add_item('sel_camp'        , "dummy")
        vals.add_item('sel_levl'        , "dummy")
        vals.add_item('sel_sess'        , "dummy")
        vals.add_item('sel_instr'        , "dummy")
        vals.add_item('sel_ptrm'        , "dummy")
        vals.add_item('sel_attr'        , "dummy")
        vals.add_item('sel_subj'        , subj)        # OVER HERE
        vals.add_item('sel_crse'        , "")
        vals.add_item('sel_title'        , "")
        vals.add_item('sel_schd'        , "%")
        vals.add_item('sel_insm'        , "%")
        vals.add_item('sel_from_cred'    , "")
        vals.add_item('sel_to_cred'        , "")
        vals.add_item('sel_camp'        , "%")
        vals.add_item('begin_hh'        , "0")
        vals.add_item('begin_mi'        , "0")
        vals.add_item('begin_ap'        , "a")
        vals.add_item('end_hh'            , "0")
        vals.add_item('end_mi'            , "0")
        vals.add_item('end_ap'            , "a")

        data = vals.get_string()

        return (url,data)