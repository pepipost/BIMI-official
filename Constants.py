"""
SVG Error Checks Regex
"""
svg_regex = {
    "REGEX_ATTRIBUTES" : r"(; expected attribute.*?\.svg:|; must be equal to.*?\.svg:|missing required attribute.*?\.svg:)",
    "REGEX_ELEMENTS" : r"(; expected the element.*?\.svg:|; expected element.*?\.svg:|missing required element.*?\.svg:)"
}
