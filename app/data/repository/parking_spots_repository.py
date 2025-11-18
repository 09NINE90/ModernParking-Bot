async def get_spot_by_id(cur, spot_num):
    cur.execute('''
                SELECT 1
                FROM dont_touch.parking_spots ps
                WHERE ps.spot_id = %s
                  AND ps.is_active = TRUE
                ''', (spot_num,))

    return cur.fetchone()