class Semester:
    def __init__(self, year, channel=None, groups=None):
        self.year = year
        self.channel = channel
        if groups:
            self.groups = list(groups)
        else:
            self.groups = []

    def __str__(self):
        return f'{self.year}.Semester'

    def __contains__(self, item):
        return item in self.groups


class StudyGroup:
    def __init__(self, name, role, semester):
        self.name = name
        self.semester = semester
        self.role = role

    def __str__(self):
        return self.name
