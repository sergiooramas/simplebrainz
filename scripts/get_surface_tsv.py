import psycopg2
"""
Given a ttf file with this script we generate a tsv with the same data
"""

ttl_path = "/path/to/dump_simplebrainz_full.n3"
dest_path = "/destination-path/"

def load_types():
    f = open(ttl_path)
    tsv_place = open(dest_path + 'surface_place.tsv', 'w')
    tsv_area = open(dest_path + 'surface_area.tsv', 'w')
    uri_to_types = dict()
    for line in f:
        data = line.strip().split(" ")
        if data and data[1].endswith("label>"):
            uri_token = data[0]
            relation = data[1]
            type_token = ' '.join(data[2:])
            token = type_token.split("\"^^")
            if '/area/' in uri_token :
                tsv_area.write(uri_token[1:-1]+"\t"+token[0][1:]+"\n")
            if '/place/' in uri_token :
                tsv_place.write(uri_token[1:-1]+"\t"+token[0][1:]+"\n")
    tsv_place.close()
    tsv_area.close()

    conn = psycopg2.connect(dbname="musicbrainz", user="postgres", password="")

    tsv_surface = open(dest_path +'surface_forms.tsv', 'w')
    cur = conn.cursor(name='artists')
    cur.itersize = 10000
    elements_added = {}
    cur.execute("select al.artist, a.gid, array_agg(al.name), a.name from musicbrainz.artist_alias al, musicbrainz.artist a where a.id=al.artist group by al.artist, a.gid, a.name;")
    more_results = True
    while more_results:
        record = cur.fetchmany(cur.itersize)
        if record:
            for alias in record:
                tsv_surface.write('http://musicbrainz.org/artist/'+alias[1] + '\t' + '\t'.join(alias[2]) + '\t' + alias[3] + '\n')
                elements_added[alias[1]] = None
        else:
            more_results = False
            cur.close()

    cur = conn.cursor(name='artists_m')
    cur.itersize = 10000

    cur.execute("select gid, name from musicbrainz.artist;")
    more_results = True
    while more_results:
        record = cur.fetchmany(cur.itersize)
        if record:
            for artist in record:
                if artist[0] not in elements_added:
                    tsv_surface.write('http://musicbrainz.org/artist/'+artist[0] + '\t' + alias[1] + '\n')
        else:
            more_results = False
            cur.close()

    elements_added = {}
    cur = conn.cursor(name='artists')
    cur.itersize = 10000
    cur.execute("select r.recording_group, array_agg(ra.name), array_agg(DISTINCT(re.name)) from musicbrainz.recording_alias ra, simplebrainz.recording_group_recording r, musicbrainz.recording re where r.recording_id=ra.recording AND r.recording_id = re.id group by r.recording_group;")
    more_results = True
    while more_results:
        record = cur.fetchmany(cur.itersize)
        if record:
            for alias in record:
                tsv_surface.write('http://musicbrainz.org/work/' + alias[0] + '\t' + '\t'.join(alias[1]) + '\t' + '\t'.join(alias[2]) + '\n')
                elements_added[alias[0]] = None
        else:
            more_results = False
            cur.close()

    cur = conn.cursor(name='artists')
    cur.itersize = 10000
    cur.execute("select r.recording_group, r.name from simplebrainz.recording_group r ;")
    more_results = True
    while more_results:
        record = cur.fetchmany(cur.itersize)
        if record:
            for alias in record:
                if alias[0] not in elements_added:
                    tsv_surface.write('http://musicbrainz.org/work/' + alias[0] + '\t' + alias[1] + '\n')
        else:
            more_results = False
            cur.close()
    
    cur = conn.cursor(name='artists')
    cur.itersize = 10000
    elements_added = {}
    cur.execute("select r.id, r.gid, array_agg(ra.name), r.name from musicbrainz.release_alias ra, musicbrainz.release_group r where r.id=ra.release group by r.id;")
    more_results = True
    while more_results:
        record = cur.fetchmany(cur.itersize)
        if record:
            for alias in record:
                tsv_surface.write('http://musicbrainz.org/release-group/' + alias[1] + '\t' + '\t'.join(alias[2]) + '\t' + alias[3] + '\n')
                elements_added[alias[1]] = None
        else:
            more_results = False
            cur.close()
    cur = conn.cursor(name='artists')
    cur.itersize = 10000
    cur.execute("select gid, name from musicbrainz.release_group ;")
    more_results = True
    while more_results:
        record = cur.fetchmany(cur.itersize)
        if record:
            for alias in record:
                if alias[0] not in elements_added:
                    tsv_surface.write('http://musicbrainz.org/release-group/' + alias[0] + '\t' + alias[1] + '\n')
        else:
            more_results = False
            cur.close()

    conn.close()
    f.close()
    


if __name__ == "__main__":
    load_types()

