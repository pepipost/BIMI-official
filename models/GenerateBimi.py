class GenerateBimi():
    def generate_bimi(self,domain, svg, vmc=""):
        if vmc!="":
            vmc = "a="+vmc
        else:
            vmc = ""

        bimi_txt_record = "_bimi."+domain+" TXT v=BIMI1; \nl="+svg+vmc
        return {"status":True, "record":bimi_txt_record,"errors":"" , "message":"BIMI record generated successfully!"}