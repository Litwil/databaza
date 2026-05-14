package com.signalnoise.ui

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.style.TextDecoration
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.signalnoise.MainViewModel
import com.signalnoise.data.Column
import com.signalnoise.data.Item
import com.signalnoise.ui.theme.*
import java.time.LocalDate
import java.time.format.DateTimeFormatter

@Composable
fun MainScreen(vm: MainViewModel, modifier: Modifier = Modifier) {
    val items by vm.items.collectAsState()
    val signalItems = items.filter { it.column == Column.SIGNAL }
    val noiseItems = items.filter { it.column == Column.NOISE }

    var addingTo by remember { mutableStateOf<Column?>(null) }

    SignalNoiseTheme {
        Box(
            modifier = modifier
                .fillMaxSize()
                .background(Background)
        ) {
            Column(modifier = Modifier.fillMaxSize()) {
                Header()
                Row(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(horizontal = 12.dp, vertical = 8.dp),
                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    ColumnPanel(
                        modifier = Modifier.weight(1f),
                        title = "Signal",
                        accent = SignalBlue,
                        dimColor = SignalBlueDim,
                        bubbleColor = SignalBlueBubble,
                        items = signalItems,
                        isSignal = true,
                        onToggle = { vm.toggleDone(it) },
                        onDelete = { vm.deleteItem(it) },
                        onAddClick = { addingTo = Column.SIGNAL }
                    )
                    ColumnPanel(
                        modifier = Modifier.weight(1f),
                        title = "Noise",
                        accent = NoiseAmber,
                        dimColor = NoiseAmberDim,
                        bubbleColor = NoiseAmberBubble,
                        items = noiseItems,
                        isSignal = false,
                        onToggle = {},
                        onDelete = { vm.deleteItem(it) },
                        onAddClick = { addingTo = Column.NOISE }
                    )
                }
            }

            if (addingTo != null) {
                AddItemSheet(
                    column = addingTo!!,
                    onAdd = { text -> vm.addItem(text, addingTo!!); addingTo = null },
                    onDismiss = { addingTo = null }
                )
            }
        }
    }
}

@Composable
private fun Header() {
    val today = LocalDate.now()
    val dayName = today.format(DateTimeFormatter.ofPattern("EEEE"))
    val date = today.format(DateTimeFormatter.ofPattern("MMM d"))

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 20.dp, vertical = 16.dp)
    ) {
        Text(
            text = dayName,
            fontSize = 13.sp,
            fontWeight = FontWeight.Medium,
            color = Subtle,
            letterSpacing = 2.sp
        )
        Text(
            text = date,
            fontSize = 28.sp,
            fontWeight = FontWeight.Bold,
            color = OnSurface
        )
        Spacer(Modifier.height(4.dp))
        HorizontalDivider(color = Surface, thickness = 1.dp)
    }
}

@Composable
private fun ColumnPanel(
    modifier: Modifier,
    title: String,
    accent: Color,
    dimColor: Color,
    bubbleColor: Color,
    items: List<Item>,
    isSignal: Boolean,
    onToggle: (Item) -> Unit,
    onDelete: (Item) -> Unit,
    onAddClick: () -> Unit
) {
    Column(modifier = modifier.fillMaxHeight()) {
        // Column header
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.padding(bottom = 10.dp)
        ) {
            Box(
                modifier = Modifier
                    .size(8.dp)
                    .clip(CircleShape)
                    .background(accent)
            )
            Spacer(Modifier.width(8.dp))
            Text(
                text = title.uppercase(),
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                color = accent,
                letterSpacing = 2.sp
            )
            Spacer(Modifier.weight(1f))
            if (items.isNotEmpty()) {
                Text(
                    text = "${items.size}",
                    fontSize = 11.sp,
                    color = Subtle,
                    modifier = Modifier
                        .clip(CircleShape)
                        .background(Surface)
                        .padding(horizontal = 6.dp, vertical = 2.dp)
                )
            }
        }

        // Items list
        LazyColumn(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(items, key = { it.id }) { item ->
                ItemBubble(
                    item = item,
                    accent = accent,
                    bubbleColor = bubbleColor,
                    isSignal = isSignal,
                    onToggle = { onToggle(item) },
                    onDelete = { onDelete(item) }
                )
            }
            item {
                Spacer(Modifier.height(8.dp))
            }
        }

        // Add button
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(14.dp))
                .background(dimColor)
                .clickable { onAddClick() }
                .padding(vertical = 12.dp),
            contentAlignment = Alignment.Center
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = Icons.Default.Add,
                    contentDescription = "Add",
                    tint = accent,
                    modifier = Modifier.size(18.dp)
                )
                Spacer(Modifier.width(6.dp))
                Text(text = "Add", fontSize = 13.sp, color = accent, fontWeight = FontWeight.SemiBold)
            }
        }
        Spacer(Modifier.height(12.dp))
    }
}

@Composable
private fun ItemBubble(
    item: Item,
    accent: Color,
    bubbleColor: Color,
    isSignal: Boolean,
    onToggle: () -> Unit,
    onDelete: () -> Unit
) {
    val alphaAnim by animateFloatAsState(
        targetValue = if (item.isDone) 0.45f else 1f,
        animationSpec = tween(300),
        label = "alpha"
    )

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(16.dp))
            .background(bubbleColor)
            .alpha(alphaAnim)
            .then(if (isSignal) Modifier.clickable { onToggle() } else Modifier)
            .padding(horizontal = 12.dp, vertical = 10.dp)
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.fillMaxWidth()
        ) {
            if (isSignal) {
                Box(
                    modifier = Modifier
                        .size(20.dp)
                        .clip(CircleShape)
                        .background(if (item.isDone) accent else Color.Transparent)
                        .border(1.5.dp, accent, CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    if (item.isDone) {
                        Icon(
                            imageVector = Icons.Default.Check,
                            contentDescription = null,
                            tint = Background,
                            modifier = Modifier.size(12.dp)
                        )
                    }
                }
                Spacer(Modifier.width(10.dp))
            }
            Text(
                text = item.text,
                fontSize = 14.sp,
                color = OnSurface,
                lineHeight = 19.sp,
                textDecoration = if (item.isDone) TextDecoration.LineThrough else TextDecoration.None,
                modifier = Modifier.weight(1f)
            )
            Spacer(Modifier.width(4.dp))
            IconButton(
                onClick = onDelete,
                modifier = Modifier.size(24.dp)
            ) {
                Icon(
                    imageVector = Icons.Default.Close,
                    contentDescription = "Delete",
                    tint = Subtle,
                    modifier = Modifier.size(14.dp)
                )
            }
        }
    }
}

@Composable
private fun AddItemSheet(
    column: Column,
    onAdd: (String) -> Unit,
    onDismiss: () -> Unit
) {
    val accent = if (column == Column.SIGNAL) SignalBlue else NoiseAmber
    val label = if (column == Column.SIGNAL) "What needs doing?" else "What's the comfort pick?"
    var text by remember { mutableStateOf("") }
    val focusRequester = remember { FocusRequester() }

    LaunchedEffect(Unit) { focusRequester.requestFocus() }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black.copy(alpha = 0.6f))
            .clickable(onClick = onDismiss),
        contentAlignment = Alignment.BottomCenter
    ) {
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .clickable(enabled = false) {},
            shape = RoundedCornerShape(topStart = 24.dp, topEnd = 24.dp),
            colors = CardDefaults.cardColors(containerColor = Surface)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(20.dp)
            ) {
                Box(
                    modifier = Modifier
                        .width(36.dp)
                        .height(4.dp)
                        .clip(CircleShape)
                        .background(Subtle)
                        .align(Alignment.CenterHorizontally)
                )
                Spacer(Modifier.height(16.dp))
                Text(
                    text = if (column == Column.SIGNAL) "Signal" else "Noise",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    color = accent,
                    letterSpacing = 2.sp
                )
                Spacer(Modifier.height(10.dp))
                OutlinedTextField(
                    value = text,
                    onValueChange = { text = it },
                    modifier = Modifier
                        .fillMaxWidth()
                        .focusRequester(focusRequester),
                    placeholder = { Text(label, color = Subtle) },
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = accent,
                        unfocusedBorderColor = Subtle,
                        cursorColor = accent,
                        focusedTextColor = OnSurface,
                        unfocusedTextColor = OnSurface
                    ),
                    shape = RoundedCornerShape(14.dp),
                    singleLine = false,
                    maxLines = 3,
                    keyboardOptions = KeyboardOptions(imeAction = ImeAction.Done),
                    keyboardActions = KeyboardActions(onDone = { if (text.isNotBlank()) onAdd(text) })
                )
                Spacer(Modifier.height(14.dp))
                Button(
                    onClick = { if (text.isNotBlank()) onAdd(text) },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(14.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = accent)
                ) {
                    Text(
                        text = "Add to ${if (column == Column.SIGNAL) "Signal" else "Noise"}",
                        color = Background,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(vertical = 4.dp)
                    )
                }
                Spacer(Modifier.height(8.dp))
            }
        }
    }
}
