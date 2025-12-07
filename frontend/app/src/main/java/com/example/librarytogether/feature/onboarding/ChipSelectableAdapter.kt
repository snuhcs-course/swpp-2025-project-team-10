package com.example.librarytogether.feature.onboarding

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.librarytogether.databinding.ItemOnboardingBubbleBinding

class ChipSelectableAdapter(
    private val onToggle: (id: Int, isSelected: Boolean) -> Unit
) : ListAdapter<ChipSelectableAdapter.Item, ChipSelectableAdapter.VH>(ItemDiffCallback()) {

    data class Item(
        val id: Int,
        val label: String
    )
    private var selectedIds = emptySet<Int>()
    fun updateSelection(newSelectedIds: Set<Int>) {
        val oldSelection = this.selectedIds
        this.selectedIds = newSelectedIds

        (oldSelection + newSelectedIds).forEach { id ->
            val position = currentList.indexOfFirst { it.id == id }
            if (position != -1) {
                notifyItemChanged(position)
            }
        }
    }

    inner class VH(private val binding: ItemOnboardingBubbleBinding) :
        RecyclerView.ViewHolder(binding.root) {

        init {
            binding.root.setOnClickListener {
                val position = bindingAdapterPosition
                if (position != RecyclerView.NO_POSITION) {
                    val item = getItem(position)
                    onToggle(item.id, !selectedIds.contains(item.id))
                }
            }
        }

        fun bind(item: Item) {
            binding.tvLabel.text = item.label

            val isSelected = selectedIds.contains(item.id)
            binding.tvLabel.isSelected = isSelected

            // 선택됨에 따라 텍스트 굵기나 색상도 변경하고 싶다면 여기서 추가 처리
            // binding.tvLabel.typeface = if (isSelected) Typeface.DEFAULT_BOLD else Typeface.DEFAULT
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val inflater = LayoutInflater.from(parent.context)
        val binding = ItemOnboardingBubbleBinding.inflate(inflater, parent, false)
        return VH(binding)
    }
    override fun onBindViewHolder(holder: VH, position: Int) {
        holder.bind(getItem(position))
    }
    class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem.id == newItem.id
        }
        override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem == newItem
        }
    }
}
