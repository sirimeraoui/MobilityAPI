import re
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

def build_collection_response(collection, base_url):
    print(collection['extent_period'])

    cleaned = re.findall(r"[-+]?\d*\.\d+|\d+", str(collection['extent']))

    # convert to float
    bbox= list(map(float, cleaned))
    return {
        "id": collection['id'],
        "title": collection['title'],
        "description": collection['description'],
        "itemType": collection['item_type'],
        "updateFrequency": collection['update_frequency'],
        "extent": None if collection['extent'] is None else {
            "spatial": {
                "bbox": bbox[:4],
                # "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
                "crs": collection['crs']
            },
            "temporal": {
                "interval": str(collection['extent_period']).strip('[]').split(', '),
            # "trs": "http://www.opengis.net/def/uom/ISO-8601/0/Gregorian"
            "trs": collection['trs']
            }
        },
 
        "links": [
            {
                "href": f"{base_url}/api/v1/collections/{collection['id']}",
                "rel": "self",
                "type": "application/json"
            },
            # {
            #     "href": f"{base_url}/collections/{collection['id']}/items", #ogc yaml mentions HTML if there is one 
            #     "rel": "items",
            #     "type": "application/json"
            # }
        ]
    }


def build_collections_list_response(collections, base_url):
    return {
        "collections": collections,
        "links": [
            {
                "href": f"{base_url}/collections",
                "rel": "self",
                "type": "application/json"
            }
        ]
    }


def fetch_collection_by_id(cursor, collection_id):
    cursor.execute("""
        SELECT c.id, c.title, c.description, c.update_frequency, c.item_type,
        extent(tg.trajectory) AS extent,
        extent(tg.trajectory)::tstzspan AS extent_period,
        ( SELECT mf.crs FROM moving_features mf WHERE mf.collection_id =  %s LIMIT 1
            ) AS crs,

        (SELECT mf.trs FROM moving_features mf WHERE mf.collection_id =  %s LIMIT 1
            ) AS trs
        FROM collections c
        LEFT JOIN temporal_geometries tg ON tg.collection_id = c.id
        WHERE c.id = %s
        GROUP BY c.id, c.title
        ORDER BY c.created_at DESC;
    """, (collection_id,collection_id,collection_id))
    
    row = cursor.fetchone()
    if not row:
        return None
    
    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, row))



# Check collection existance by ID:
def collection_exists(cursor, collection_id):
    cursor.execute(
        "SELECT id FROM collections WHERE id = %s",
        (collection_id,)
    )
    return cursor.fetchone() is not None


#________________________________rr
def insert_collection(cursor, collection_id, data):
    cursor.execute("""
        INSERT INTO collections 
        (id, title, description, update_frequency, item_type)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (
        collection_id,
        data.get("title"),
        data.get("description"),
        data.get("updateFrequency"),
        data.get("itemType", "movingfeature")
    ))
    return cursor.fetchone()[0]

def update_collection(cursor, collection_id, data):
    updates = []
    values = []

    if "title" in data:
        updates.append("title = %s")
        values.append(data["title"])
    if "description" in data:
        updates.append("description = %s")
        values.append(data["description"])
    if "itemType" in data:
        updates.append("item_type = %s")
        values.append(data["itemType"])

    if not updates:
        return False

    updates.append("updated_at = NOW()")

    values.append(collection_id)

    cursor.execute(
        f"""
        UPDATE collections
        SET {', '.join(updates)}
        WHERE id = %s
        """,
        values,
    )

    return True