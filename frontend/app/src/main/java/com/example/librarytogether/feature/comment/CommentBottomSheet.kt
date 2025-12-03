package com.example.librarytogether.feature.comment

import android.app.Dialog
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.WindowManager
import androidx.appcompat.app.AlertDialog
import androidx.fragment.app.activityViewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.librarytogether.databinding.CommentBinding
import com.example.librarytogether.feature.comment.data.CommentDto
import com.example.librarytogether.feature.home.data.Post
import com.google.android.material.bottomsheet.BottomSheetBehavior
import com.google.android.material.bottomsheet.BottomSheetDialog
import com.google.android.material.bottomsheet.BottomSheetDialogFragment
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class CommentBottomSheet : BottomSheetDialogFragment() {

    private var _binding: CommentBinding? = null
    private val binding get() = _binding!!

    private val viewModel: CommentViewModel by activityViewModels()

    private lateinit var adapter: CommentAdapter
    private lateinit var post: Post

    private var currentUserName = "You" // TODO: 실제 사용자 이름으로 교체 필요

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // PostDto가 아닌 Post(프론트 DTO) 전달받음
        post = requireArguments().getSerializable("post") as Post

        // ViewModel 초기화
        viewModel.initialize(post)
    }

    override fun onCreateDialog(savedInstanceState: Bundle?): Dialog {
        val dialog = super.onCreateDialog(savedInstanceState) as BottomSheetDialog

        dialog.setOnShowListener { dialogInterface ->
            val bottomSheetDialog = dialogInterface as BottomSheetDialog
            val bottomSheet =
                bottomSheetDialog.findViewById<View>(
                    com.google.android.material.R.id.design_bottom_sheet
                )

            bottomSheet?.let { sheet ->
                sheet.background = null
                val behavior = BottomSheetBehavior.from(sheet)
                behavior.state = BottomSheetBehavior.STATE_EXPANDED
                behavior.skipCollapsed = true
                behavior.isDraggable = true
            }
        }

        return dialog
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = CommentBinding.inflate(inflater, container, false)

        dialog?.window?.setSoftInputMode(
            WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE
        )

        return binding.root
    }

    override fun onStart() {
        super.onStart()

        val sheetDialog = dialog as? BottomSheetDialog
        val bottomSheet =
            sheetDialog?.findViewById<View>(
                com.google.android.material.R.id.design_bottom_sheet
            )

        bottomSheet?.let { sheet ->
            val height = (resources.displayMetrics.heightPixels * 0.85).toInt()
            val layoutParams = sheet.layoutParams
            layoutParams.height = height
            sheet.layoutParams = layoutParams

            val behavior = BottomSheetBehavior.from(sheet)
            behavior.state = BottomSheetBehavior.STATE_EXPANDED
        }
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {

        adapter = CommentAdapter(
            items = mutableListOf(),
            currentUserName = currentUserName,
            onDelete = { dto -> showDeleteDialog(dto) },
            onEdit = { dto -> showEditDialog(dto) }
        )

        binding.recyclerComments.layoutManager =
            LinearLayoutManager(requireContext())
        binding.recyclerComments.adapter = adapter

        viewModel.comments.observe(viewLifecycleOwner) { list ->
            adapter.updateComments(list)
            updateEmptyState(list)
        }

        binding.btnSend.setOnClickListener {
            val text = binding.etComment.text.toString().trim()
            if (text.isNotEmpty()) {
                viewModel.writeComment(text)
                binding.etComment.setText("")
            }
        }
    }

    private fun updateEmptyState(list: List<CommentDto>) {
        binding.emptyMessage.visibility =
            if (list.isEmpty()) View.VISIBLE else View.GONE
    }

    private fun showDeleteDialog(dto: CommentDto) {
        AlertDialog.Builder(requireContext())
            .setMessage("댓글을 삭제할까요?")
            .setPositiveButton("삭제") { _, _ ->
                viewModel.deleteComment(dto)
            }
            .setNegativeButton("취소", null)
            .show()
    }

    private fun showEditDialog(dto: CommentDto) {
        val editText = android.widget.EditText(requireContext()).apply {
            setText(dto.content)
            setSelection(dto.content.length)
        }

        AlertDialog.Builder(requireContext())
            .setTitle("댓글 수정")
            .setView(editText)
            .setPositiveButton("저장") { _, _ ->
                val newContent = editText.text.toString().trim()
                if (newContent.isNotEmpty()) {
                    viewModel.editComment(dto.id, newContent)
                }
            }
            .setNegativeButton("취소", null)
            .show()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }

    companion object {
        fun newInstance(post: Post) = CommentBottomSheet().apply {
            arguments = Bundle().apply {
                putSerializable("post", post)
            }
        }
    }
}
