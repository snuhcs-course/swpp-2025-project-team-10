package com.example.librarytogether.feature.comment

import android.app.Dialog
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.WindowManager
import android.widget.EditText
import androidx.appcompat.app.AlertDialog
import androidx.core.os.bundleOf
import androidx.fragment.app.activityViewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.librarytogether.databinding.CommentBinding
import com.example.librarytogether.feature.comment.data.CommentDto
import com.google.android.material.bottomsheet.BottomSheetDialog
import com.google.android.material.bottomsheet.BottomSheetDialogFragment
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class CommentBottomSheet : BottomSheetDialogFragment() {

    private var _binding: CommentBinding? = null
    private val binding get() = _binding!!

    private val vm: CommentViewModel by activityViewModels()
    private lateinit var adapter: CommentAdapter

    private var postId: Int = -1
    private var initialComments: List<CommentDto> = emptyList()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        postId = requireArguments().getInt("postId")
        @Suppress("UNCHECKED_CAST")
        initialComments = requireArguments().getSerializable("comments") as ArrayList<CommentDto>

        vm.initialize(postId, initialComments)
    }

    override fun onCreateDialog(savedInstanceState: Bundle?): Dialog =
        BottomSheetDialog(requireContext()).apply {
            setOnShowListener {
                val sheet = findViewById<View>(com.google.android.material.R.id.design_bottom_sheet)
                sheet?.let {
                    it.layoutParams.height =
                        (resources.displayMetrics.heightPixels * 0.85).toInt()
                }
            }
        }

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = CommentBinding.inflate(inflater, container, false)
        dialog?.window?.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {

        adapter = CommentAdapter(
            items = mutableListOf(),
            currentUserName = "You", // TODO
            onLike = { dto -> vm.toggleLike(dto) },
            onDelete = { dto -> showDeleteDialog(dto) },
            onEdit = { dto -> showEditDialog(dto) }
        )

        binding.recyclerComments.layoutManager = LinearLayoutManager(requireContext())
        binding.recyclerComments.adapter = adapter

        vm.comments.observe(viewLifecycleOwner) { list ->
            adapter.updateComments(list)
        }

        binding.btnSend.setOnClickListener {
            val txt = binding.etComment.text.toString().trim()
            if (txt.isNotEmpty()) {
                vm.writeComment(txt)
                binding.etComment.setText("")
            }
        }
    }

    private fun showDeleteDialog(dto: CommentDto) {
        AlertDialog.Builder(requireContext())
            .setMessage("댓글을 삭제할까요?")
            .setPositiveButton("삭제") { _, _ -> vm.deleteComment(dto) }
            .setNegativeButton("취소", null)
            .show()
    }

    private fun showEditDialog(dto: CommentDto) {
        val edit = EditText(requireContext())
        edit.setText(dto.content)

        AlertDialog.Builder(requireContext())
            .setTitle("댓글 수정")
            .setView(edit)
            .setPositiveButton("저장") { _, _ ->
                val new = edit.text.toString().trim()
                if (new.isNotEmpty()) vm.editComment(dto.id, new)
            }
            .setNegativeButton("취소", null)
            .show()
    }

    companion object {
        fun newInstance(postId: Int, comments: List<CommentDto>) =
            CommentBottomSheet().apply {
                arguments = bundleOf(
                    "postId" to postId,
                    "comments" to ArrayList(comments)
                )
            }
    }
}

private fun CommentBottomSheet.initializeWithArgsForTest(
    i: Int,
    initial: kotlin.collections.List<com.example.librarytogether.feature.comment.data.CommentDto>
) {
}
