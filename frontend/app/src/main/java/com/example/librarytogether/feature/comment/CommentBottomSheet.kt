package com.example.librarytogether.feature.comment

import android.app.Dialog
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
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
    }

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = CommentBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        vm.initialize(postId, initialComments)

        val sharedPrefs = requireContext().getSharedPreferences("app_prefs", android.content.Context.MODE_PRIVATE)
        val myName = sharedPrefs.getString("username", "") ?: ""

        Log.d("CommentSheet", "내 이름 확인: $myName")

        adapter = CommentAdapter(
            items = mutableListOf(),
            currentUserName = myName,
            onLike = { dto -> vm.toggleLike(dto) },
            onDelete = { dto -> showDeleteDialog(dto) },
            onEdit = { dto -> showEditDialog(dto) }
        )

        binding.recyclerComments.layoutManager = LinearLayoutManager(requireContext())
        binding.recyclerComments.adapter = adapter

        vm.comments.observe(viewLifecycleOwner) { list ->
            adapter.updateComments(list)

            // 댓글 없을 때 UI
            binding.emptyMessage.isVisible = list.isEmpty()
            binding.recyclerComments.isVisible = list.isNotEmpty()

            if (list.size > initialComments.size) {
                binding.etComment.setText("")
            }
        }

        // 전송 버튼
        binding.btnSend.setOnClickListener {
            val content = binding.etComment.text.toString().trim()
            if (content.isNotEmpty()) vm.writeComment(content)
        }
    }
    // 다이얼로그: 창 크기를 화면의 90%로 설정
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

    private fun showDeleteDialog(dto: CommentDto) {
        AlertDialog.Builder(requireContext())
            .setTitle("댓글 삭제")
            .setMessage("정말 삭제하시겠습니까?")
            .setPositiveButton("삭제") { _, _ -> vm.deleteComment(dto) }
            .setNegativeButton("취소", null)
            .show()
    }

    private fun showEditDialog(dto: CommentDto) {
        val edit = EditText(requireContext())
        edit.setText(dto.content)
        val container = android.widget.FrameLayout(requireContext())
        val params = android.widget.FrameLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.WRAP_CONTENT
        )
        params.leftMargin = 50; params.rightMargin = 50
        edit.layoutParams = params
        container.addView(edit)

        AlertDialog.Builder(requireContext())
            .setTitle("댓글 수정")
            .setView(container)
            .setPositiveButton("저장") { _, _ ->
                val newContent = edit.text.toString().trim()
                if (newContent.isNotEmpty()) {
                    vm.editComment(dto.id, newContent)
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
        private const val ARG_POST_ID = "arg_post_id"
        private const val ARG_COMMENTS = "arg_comments"

        fun newInstance(postId: Int, comments: List<CommentDto>?): CommentBottomSheet {
            val fragment = CommentBottomSheet()
            val args = Bundle().apply {
                putInt(ARG_POST_ID, postId)
                val commentsArrayList = if (comments != null) ArrayList(comments) else ArrayList()
                putSerializable(ARG_COMMENTS, commentsArrayList)
            }
            fragment.arguments = args
            return fragment
        }
    }
}
