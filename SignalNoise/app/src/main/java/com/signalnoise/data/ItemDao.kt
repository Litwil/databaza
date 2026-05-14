package com.signalnoise.data

import androidx.room.*
import kotlinx.coroutines.flow.Flow

@Dao
interface ItemDao {
    @Query("SELECT * FROM items WHERE dateKey = :dateKey ORDER BY createdAt ASC")
    fun getItemsForDay(dateKey: String): Flow<List<Item>>

    @Insert
    suspend fun insert(item: Item)

    @Update
    suspend fun update(item: Item)

    @Delete
    suspend fun delete(item: Item)

    @Query("DELETE FROM items WHERE dateKey = :dateKey")
    suspend fun clearDay(dateKey: String)
}
