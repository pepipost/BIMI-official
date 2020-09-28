class GenerateBimi:
    def generate_bimi(self,domain, svg, vmc=""):
        if vmc!="":
            vmc = vmc+";"
        else:
            vmc = ";"

        bimi_txt_record = "default._bimi."+domain+" TXT v=BIMI1; \nl="+svg+"; a="+vmc
        return {"status":True, "record":bimi_txt_record,"errors":[""] , "message":"BIMI record generated successfully!!!"}