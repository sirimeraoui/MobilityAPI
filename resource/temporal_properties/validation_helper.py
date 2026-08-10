#validate resources exist by ids::::::::::::::::::::::::::::::::::::::::::::::::::::::
def validate_collection_exists(cursor, collection_id):
    cursor.execute(
        "SELECT id FROM collections WHERE id = %s",
        (collection_id,)
    )
    return cursor.fetchone() is not None

def validate_feature_exists(cursor, feature_id, collection_id):
    cursor.execute(
        "SELECT id FROM moving_features WHERE id = %s AND collection_id = %s",
        (feature_id, collection_id)
    )
    return cursor.fetchone() is not None

def validate_property_exists(cursor, feature_id, property_name):
    cursor.execute("""
        SELECT id FROM temporal_properties
        WHERE feature_id = %s AND property_name = %s
    """, (feature_id, property_name))
    return cursor.fetchone()
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

def validate_temporal_continuity(cursor, property_id, first_new_time):
    cursor.execute("""
        SELECT MAX(datetimes[array_length(datetimes, 1)]) as last_time
        FROM temporal_values
        WHERE property_id = %s
    """, (property_id,))
    
    last_time_row = cursor.fetchone()
    if last_time_row and last_time_row[0]:
        last_time = last_time_row[0]
        if last_time >= first_new_time:
            return False, last_time
    return True, None
