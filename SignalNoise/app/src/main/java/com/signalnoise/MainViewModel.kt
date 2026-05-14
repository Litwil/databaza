package com.signalnoise

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.signalnoise.data.AppDatabase
import com.signalnoise.data.Column
import com.signalnoise.data.Item
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import java.time.LocalDate

class MainViewModel(app: Application) : AndroidViewModel(app) {

    private val dao = AppDatabase.get(app).itemDao()
    val todayKey: String = LocalDate.now().toString()

    val items = dao.getItemsForDay(todayKey)
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    fun addItem(text: String, column: Column) {
        if (text.isBlank()) return
        viewModelScope.launch {
            dao.insert(Item(text = text.trim(), column = column, dateKey = todayKey))
        }
    }

    fun toggleDone(item: Item) {
        viewModelScope.launch { dao.update(item.copy(isDone = !item.isDone)) }
    }

    fun deleteItem(item: Item) {
        viewModelScope.launch { dao.delete(item) }
    }

    fun clearToday() {
        viewModelScope.launch { dao.clearDay(todayKey) }
    }
}
