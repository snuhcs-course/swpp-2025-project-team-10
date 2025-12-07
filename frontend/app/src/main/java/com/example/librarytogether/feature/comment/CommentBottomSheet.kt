package com.example.librarytogether.feature.comment

import android.app.Dialog
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.WindowManager
import android.widget.EditText
import androidx.appcompat.app.AlertDialog
import androidx.core.view.isVisible
import androidx.fragment.app.activityViewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.librarytogether.databinding.CommentBinding
import com.example.librarytogether.feature.comment.data.CommentDto
import com.google.android.material.bottomsheet.BottomSheetBehavior
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

        arguments?.let { args ->
            postId = args.getInt(ARG_POST_ID, -1)

            @Suppress("UNCHECKED_CAST")
            initialComments = (args.getSerializable(ARG_COMMENTS) as? ArrayList<CommentDto>) ?: emptyList()
        }

        if (postId != -1) {
            vm.initialize(postId, initialComments)
        }
    }

    override fun onCreateDialog(savedInstanceState: Bundle?): Dialog {
        val dialog = BottomSheetDialog(requireContext(), theme)
        dialog.setOnShowListener {
            val bottomSheet = (it as BottomSheetDialog)
                .findViewById<View>(com.google.android.material.R.id.design_bottom_sheet)

            bottomSheet?.let { sheet ->
                val behavior = BottomSheetBehavior.from(sheet)
                val displayMetrics = resources.displayMetrics
                val screenHeight = displayMetrics.heightPixels
                val layoutParams = sheet.layoutParams

                layoutParams.height = (screenHeight * 0.90).toInt()
                sheet.layoutParams = layoutParams

                behavior.state = BottomSheetBehavior.STATE_EXPANDED
                behavior.skipCollapsed = true
            }
        }
        return dialog
    }


    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = CommentBinding.inflate(inflater, container, false)
        dialog?.window?.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        adapter = CommentAdapter(
            items = mutableListOf(),
            currentUserName = "You", // TODO: 실제 사용자 이름으로 변경 필요
            onLike = { dto -> vm.toggleLike(dto) },
            onDelete = { dto -> showDeleteDialog(dto) },
            onEdit = { dto -> showEditDialog(dto) }
        )

        binding.recyclerComments.layoutManager = LinearLayoutManager(requireContext())
        binding.recyclerComments.adapter = adapter

        vm.comments.observe(viewLifecycleOwner) { list ->
            // 로그: UI에 데이터가 도달했는지 확인
            android.util.Log.d("BottomSheet", "UI 업데이트. 댓글 개수: ${list.size}")

            adapter.updateComments(list)
            binding.emptyMessage.isVisible = list.isEmpty()
            binding.recyclerComments.isVisible = list.isNotEmpty()

            // 댓글 전송 후 입력창 비우기 (리스트가 갱신되었다는 건 전송 성공을 의미)
            if (list.isNotEmpty()) {
                binding.etComment.setText("")
            }
        }
        // 2. [추가] 에러 메시지 관찰 (Toast 띄우기)
        vm.error.observe(viewLifecycleOwner) { msg ->
            if (!msg.isNullOrEmpty()) {
                android.widget.Toast.makeText(context, msg, android.widget.Toast.LENGTH_LONG).show()
            }
        }

        binding.btnSend.setOnClickListener {
            val txt = binding.etComment.text.toString().trim()
            if (txt.isNotEmpty()) {
                vm.writeComment(txt)
                binding.etComment.setText("")
            }
        }
    }
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
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
                val newContent = edit.text.toString().trim()
                if (newContent.isNotEmpty()) {
                    vm.editComment(dto.id, newContent)
                }
            }
            .setNegativeButton("취소", null)
            .show()
    }

    companion object {
        private const val ARG_POST_ID = "arg_post_id"
        private const val ARG_COMMENTS = "arg_comments"

        /**
         * @param postId 게시글 ID
         * @param comments 댓글 리스트 (null 허용, null인 경우 빈 리스트로 처리됨)
         */
        fun newInstance(postId: Int, comments: List<CommentDto>?): CommentBottomSheet {
            val fragment = CommentBottomSheet()
            val args = Bundle().apply {
                putInt(ARG_POST_ID, postId)
                // comments가 null이면 빈 ArrayList를 넣고, 아니면 ArrayList로 변환하여 넣음
                val commentsArrayList = if (comments != null) ArrayList(comments) else ArrayList()
                putSerializable(ARG_COMMENTS, commentsArrayList)
            }
            fragment.arguments = args
            return fragment
        }
    }
}

private fun CommentBottomSheet.initializeWithArgsForTest(
    i: Int,
    initial: kotlin.collections.List<com.example.librarytogether.feature.comment.data.CommentDto>
) {
}
