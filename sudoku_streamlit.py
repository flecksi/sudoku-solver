from sudoku import SudokuBoard
import streamlit as st
import pandas as pd
from sudoku_svg import create_svg

st.set_page_config(page_title="Sudoku", layout="wide")

st.title("Create and Solve Sudokus")

if "board" not in st.session_state:
    st.session_state["board"] = SudokuBoard.random(n_places_to_fill=40)

c1, c2, c3, c4, c5 = st.columns(5)
if c1.button("Easy", use_container_width=True, type="primary"):
    st.session_state["board"] = SudokuBoard.random(n_places_to_fill=45)
if c2.button("Medium", use_container_width=True, type="primary"):
    st.session_state["board"] = SudokuBoard.random(n_places_to_fill=35)
if c3.button("Hard", use_container_width=True, type="primary"):
    st.session_state["board"] = SudokuBoard.random(n_places_to_fill=28)
if c4.button("Full", use_container_width=True, type="secondary"):
    st.session_state["board"] = SudokuBoard.random(n_places_to_fill=81)
if c5.button("Empty", use_container_width=True, type="secondary"):
    st.session_state["board"] = SudokuBoard.empty()

    # st.code(body=" " + board.draw(indent=0, zero_char=" ", hfill=0))

# c_left1, c_right1 = st.columns(2)

# c_left1.image(
#     create_svg(
#         cells=st.session_state["board"].cells,
#         qr_data=st.session_state["board"].solve()[0].draw(hfill=0),
#     ).as_svg(),
#     use_column_width=True,
# )

c_left1, c_right1 = st.columns(2)

df_board = st.session_state["board"].as_dataframe()
df_board.replace(0, pd.NA, inplace=True)

c_right1.subheader("Enter numbers here:")
df_filled = c_right1.data_editor(
    df_board,
    hide_index=True,
    # use_container_width=True,
    column_config={
        col: st.column_config.NumberColumn(min_value=1, max_value=9, step=1)
        for col in ("A", "B", "C", "D", "E", "F", "G", "H", "I")
    },
)
c_right1.markdown(
    "You can create or solve any Sudoku by entering numbers into an empty board."
)

# st.subheader("Filled board")
# st.dataframe(df_filled)


# st.write(df_filled.loc[0, "1"])

# board_filled = SudokuBoard.from_dataframe(df_board)

board_filled = SudokuBoard.from_dataframe(df_filled)
boards_solved = board_filled.solve()
board_filled_ok = len(boards_solved) > 0
board_filled_fully = board_filled.n_filled == 81

bg_color = "none"
if not board_filled_ok:
    bg_color = "red"
elif board_filled_fully:
    bg_color = "green"

c_left1.image(
    create_svg(
        cells=board_filled.cells,
        qr_data=(
            boards_solved[0].draw(hfill=0) if board_filled_ok else "No Valid Solution"
        ),
        bg_color=bg_color,  # "none" if board_filled_ok else "red",
        # bg_color="green" if board_filled.n_filled == 81 else "none",
    ).as_svg(),
    use_column_width=True,
)

# st.progress(board_filled.n_filled / 81, text=f"{board_filled.n_filled}/81")

# if st.checkbox("Show Validity", value=True):
#     # st.code(board_filled.draw())
#     if board_filled_ok:
#         st.success("Looks OK")
#     else:
#         st.error("Looks not OK")

if st.checkbox("Show Solution", value=False):
    if len(boards_solved) == 0:
        st.error("No Solution!")
    else:
        c_left2, c_right2 = st.columns(2)

        board_solved = boards_solved[0]
        # st.dataframe(
        #     board_solved.as_dataframe(),
        #     # use_container_width=True,
        #     hide_index=True,
        # )

        c_left2.image(
            create_svg(
                cells=board_solved.cells,
                qr_data=(board_solved.draw(hfill=0)),
                include_qr_solution=True,
            ).as_svg(),
            use_column_width=True,
        )
