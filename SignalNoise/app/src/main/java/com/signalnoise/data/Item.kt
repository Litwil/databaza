package com.signalnoise.data

import androidx.room.Entity
import androidx.room.PrimaryKey

enum class Column { SIGNAL, NOISE }

@Entity(tableName = "items")
data class Item(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val text: String,
    val column: Column,
    val isDone: Boolean = false,
    val createdAt: Long = System.currentTimeMillis(),
    val dateKey: String  // "YYYY-MM-DD" — used to bucket items per day
)
