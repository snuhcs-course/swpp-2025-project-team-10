package com.example.librarytogether.feature.comment

import android.app.Dialog
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.WindowManager
import android.widget.FrameLayout
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

    private val viewModel: CommentViewModel by activityViewModels()
    private lateinit var adapter: CommentAdapter

    private var postId: Int = -1
    private var currentUserName = "You"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        postId = requireArguments().getInt("postId")
        // 스타일 적용 (배경 투명화가 안 될 경우를 대비해 스타일도 지정 가능)
        // setStyle(STYLE_NORMAL, R.style.CustomBottomSheetDialogTheme)
    }

    // ★ 핵심 수정 부분: 다이얼로그 생성 시점 설정
    override fun onCreateDialog(savedInstanceState: Bundle?): Dialog {
        val dialog = super.onCreateDialog(savedInstanceState) as BottomSheetDialog

        dialog.setOnShowListener { dialogInterface ->
            val bottomSheetDialog = dialogInterface as BottomSheetDialog
            val bottomSheet = bottomSheetDialog.findViewById<View>(com.google.android.material.R.id.design_bottom_sheet) as FrameLayout?

            bottomSheet?.let { sheet ->
                // 1. 배경 투명화 (XML에서 만든 둥근 배경이 잘 보이도록)
                sheet.background = null

                // 2. 동작 설정 (화면 꽉 차게 펼치기)
                val behavior = BottomSheetBehavior.from(sheet)
                behavior.state = BottomSheetBehavior.STATE_EXPANDED
                behavior.skipCollapsed = true // 접히는 단계 건너뛰기
                behavior.isDraggable = true   // 드래그로 닫기 가능
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

        // ★ 키보드 올라올 때 입력창이 가려지지 않게 설정
        dialog?.window?.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE)

        return binding.root
    }

    override fun onStart() {
        super.onStart()

        val sheetDialog = dialog as? BottomSheetDialog
        val bottomSheet = sheetDialog?.findViewById<View>(com.google.android.material.R.id.design_bottom_sheet)

        bottomSheet?.let { sheet ->
            // 1. 화면 전체 높이 구하기
            val displayMetrics = resources.displayMetrics
            val windowHeight = displayMetrics.heightPixels

            // 2. 바텀 시트의 높이를 화면의 85% (또는 원하시면 MATCH_PARENT)로 강제 고정
            val layoutParams = sheet.layoutParams
            layoutParams.height = (windowHeight * 0.85).toInt() // 원하는 비율 (예: 0.9, 1.0 등)
            sheet.layoutParams = layoutParams

            // 3. 상태를 '펼침(EXPANDED)'으로 고정
            val behavior = BottomSheetBehavior.from(sheet)
            behavior.state = BottomSheetBehavior.STATE_EXPANDED
            behavior.skipCollapsed = true // 접힌 상태 무시
        }
    }
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        adapter = CommentAdapter(mutableListOf())
        binding.recyclerComments.layoutManager = LinearLayoutManager(requireContext())
        binding.recyclerComments.adapter = adapter

        viewModel.loadComments(postId)

        viewModel.comments.observe(viewLifecycleOwner) { list ->
            adapter.updateComments(list)
            updateEmptyState(list)

            // 데이터 로드 시 맨 아래로 스크롤 (선택 사항)
            // if (list.isNotEmpty()) binding.recyclerComments.scrollToPosition(list.size - 1)
        }

        binding.btnSend.setOnClickListener {
            val text = binding.etComment.text.toString().trim()
            if (text.isNotEmpty()) {
                viewModel.writeComment(postId, text)
                viewModel.addCommentLocal(text, currentUserName)

                binding.etComment.setText("")

                // ★ 편의 기능: 댓글 작성 후 리스트 맨 아래로 스크롤
                binding.recyclerComments.post {
                    if (adapter.itemCount > 0) {
                        binding.recyclerComments.smoothScrollToPosition(adapter.itemCount - 1)
                    }
                }
            }
        }
    }

    private fun updateEmptyState(list: List<CommentDto>) {
        if (list.isEmpty()) {
            binding.emptyMessage.visibility = View.VISIBLE
        } else {
            binding.emptyMessage.visibility = View.GONE
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }

    companion object {
        fun newInstance(postId: Int) = CommentBottomSheet().apply {
            arguments = Bundle().apply { putInt("postId", postId) }
        }
    }
}
