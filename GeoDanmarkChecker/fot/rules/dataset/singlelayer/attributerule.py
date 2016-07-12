from .singlefeaturerule import SingleFeatureRule


class AttributeRule(SingleFeatureRule):

    def __init__(self, name, feature_type, attributename, isvalidfunction, filter=None):
        super(AttributeRule, self).__init__(name, feature_type, attributesneeded=[attributename], geometryneeded=True)
        self.attributename = attributename
        self.isvalidfunction = isvalidfunction

    def check(self, feature, reporter):
        try:
            value = feature[self.attributename]
            if not self.isvalidfunction(value):
                reporter.error(self.name, self.featuretype, self.attributename + "=" + unicode(value) + " not valid", feature)
        except:
            reporter.error(self.name, self.featuretype, "Error processing attribute: " + self.attributename, feature)
