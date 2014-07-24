import csv
import sys

BUNDLE_GENRE = 0
BUNDLE_GENRE_CHANNEL = 1


def read_csv_file(filename):
    filestream = open(filename, 'rU')
    csvreader = csv.reader(filestream)

    csvrows = []
    for row in csvreader:
        csvrows.append(row)

    filestream.close()

    return csvrows


class Affinity:

    def __init__(self, csvfile, bundling=BUNDLE_GENRE):
        self._rows = read_csv_file(csvfile)[1:]
        self._bundling = bundling
        self._genres = self._count_genres()
        self._userids = self._count_userids()

    @property
    def userids(self):
        return list(self._userids.iterkeys())

    @property
    def genres(self):
        l = list(self._genres.iterkeys())
        l.remove('_total')
        return l

    def _count_genres(self):
        genres = {}
        genres['_total'] = 0
        seen_programmes = []

        for row in self._rows:
            if row[2] in seen_programmes:
                continue
            else:
                seen_programmes.append(row[2])

            genres['_total'] += 1

            rowgenres = row[9].split(', ')
            for genre in rowgenres:
                eff_genre = self._row_to_eff_genre(row, genre)
                if eff_genre in genres:
                    genres[eff_genre] += 1
                else:
                    genres[eff_genre] = 1

        return genres

    def _row_to_eff_genre(self, row, genre):
        if self._bundling == BUNDLE_GENRE:
            return genre
        elif self._bundling == BUNDLE_GENRE_CHANNEL:
            return row[5].upper() + " " + genre

    def _count_userids(self):
        userids = {}

        for row in self._rows:
            if row[0] not in userids:
                user = userids[row[0]] = {}
                user['_total'] = 0
                for genre in self._genres.iterkeys():
                    if genre != '_total':
                        user[genre] = 0
            else:
                user = userids[row[0]]

            user['_total'] += 1

            rowgenres = row[9].split(', ')
            for genre in rowgenres:
                eff_genre = self._row_to_eff_genre(row, genre)
                if eff_genre in user:
                    user[eff_genre] += 1
                else:
                    user[eff_genre] = 1

        return userids

    def affinity(self, userid, genre):
        genre = genre.upper()
        userid = str(userid)

        a = float(self._userids[userid][genre]) / self._userids[userid]['_total']
        b = float(self._genres[genre]) / self._genres['_total']

        if a >= b:
            return (a - b) / (1 - b)
        elif a < b:
            return -((b - a) / b)

    def numwatched(self, userid, genre):
        return self._userids[userid][genre]

    def numgenre(self, genre):
        return self._genres[genre.upper()]

if __name__ == '__main__':
    affinity = Affinity(sys.argv[1], BUNDLE_GENRE_CHANNEL)

    for userid in affinity.userids:
        print "Affinity for userid " + userid + ":"
        for genre in affinity.genres:
            print genre + ": " + str(affinity.affinity(userid, genre)) + " (" + str(affinity.numwatched(userid, genre)) + "/" + str(affinity.numgenre(genre)) + " watched)"
        print
