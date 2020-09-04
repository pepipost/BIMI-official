from lxml import etree
import xml.etree.cElementTree as et
# from io import StringIO
class CheckSvg:
    def __init__(self):
        self.RNG_SCHEMA_FILE = "svg_schema/relaxng.rng.xml"

    # CHECK SVG TAG
    def is_svg_extension(self, file):
        if file.endswith('.svg') or file.endswith('.SVG'):
            return True
        else:
            return False

    def is_svg_xml(self, filename):
        tag = None
        with open(filename, "r") as f:
            try:
                for event, el in et.iterparse(f, ('start',)):
                    tag = el.tag
                    break
            except et.ParseError:
                pass
        return tag == '{http://www.w3.org/2000/svg}svg'

    def check_svg(self, file_svg):
        if self.is_svg_extension(file_svg):
            if self.is_svg_xml(file_svg):
                return "Valid SVG"
                # if self.is_svg_schema(file_svg):
                #     return "Valid SVG file"
                # else:
                #     return "Invalid SVG Schema"
            else:
                return "Invalid SVG"
        else:
            return "Not an SVG extension"

    def chec_svg_schema(self, file_svg):
        with open(self.RNG_SCHEMA_FILE) as f:
            relaxng_doc = etree.parse(f)
        
        relaxng = etree.RelaxNG(relaxng_doc)

        with open(file_svg) as valid:
            doc = etree.parse(valid)
        return relaxng.validate(doc)

        """f = StringIO('''\
                        <element name="a" xmlns="http://relaxng.org/ns/structure/1.0">
                        <zeroOrMore>
                            <element name="b">
                            <text />
                            </element>
                        </zeroOrMore>
                        </element>
                    ''')
        relaxng_doc = etree.parse(f)
        relaxng = etree.RelaxNG(relaxng_doc)

        with open(file_svg) as svg:
            doc = etree.parse(svg)
        relaxng.validate(doc)"""