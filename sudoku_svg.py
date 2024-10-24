import drawsvg as draw
import qrcode
import qrcode.image.svg


def create_svg(
    cells: list[list[int]],
    qr_data: str = "No Data Provided",
    bg_color: str = "none",
    include_qr_solution: bool = True,
):
    cell_size = 40
    board_size = cell_size * 9
    padding = 10
    drawing_size = board_size + (2 * padding)

    box_bg_color1 = "orange"
    box_bg_color2 = "yellow"
    box_bg_opacity1 = 0.5
    box_bg_opacity2 = 0.5
    thin_line_width = 1
    thick_line_width = 3

    fontsize = cell_size
    numbercolor = "black"

    qr_size = cell_size * 3

    drawing_width = drawing_size + (qr_size + padding if include_qr_solution else 0)
    s = draw.Drawing(width=drawing_width, height=drawing_size)

    background = draw.Rectangle(
        0, 0, drawing_width, drawing_size, stroke="none", fill=bg_color
    )
    s.append(background)

    # box-background
    for r in range(3):
        for c in range(3):
            if (r + c) % 2 == 0:
                box_bg_color = box_bg_color1
                box_bg_opacity = box_bg_opacity1

            else:
                box_bg_color = box_bg_color2
                box_bg_opacity = box_bg_opacity2

            box_size = cell_size * 3
            x_start = padding + box_size * c
            y_start = padding + box_size * r

            s.append(
                draw.Rectangle(
                    x_start,
                    y_start,
                    box_size,
                    box_size,
                    stroke="none",
                    fill=box_bg_color,
                    fill_opacity=box_bg_opacity,
                )
            )

    outer_square = draw.Rectangle(
        padding,
        padding,
        board_size,
        board_size,
        stroke_width=thick_line_width,
        stroke="black",
        fill="none",
    )
    s.append(outer_square)

    # thin gridlines
    for i in range(1, 9):
        line_thickness = thin_line_width
        if i % 3 == 0:
            line_thickness = thick_line_width

        coord = padding + i * cell_size
        h_gridline = draw.Line(
            padding,
            coord,
            padding + board_size,
            coord,
            stroke_width=line_thickness,
            stroke="black",
            fill="none",
        )
        s.append(h_gridline)
        v_gridline = draw.Line(
            coord,
            padding,
            coord,
            padding + board_size,
            stroke_width=line_thickness,
            stroke="black",
            fill="none",
        )
        s.append(v_gridline)

    for row in range(9):
        for col in range(9):
            cell_value = cells[row][col]

            if cell_value != 0:
                s.append(
                    draw.Text(
                        str(cell_value),
                        fontsize,
                        padding + (cell_size // 2) + (col * cell_size),
                        padding + (cell_size // 2) + (row * cell_size),
                        text_anchor="middle",
                        dominant_baseline="central",  # "middle",#
                        fill=numbercolor,
                    )
                )

    if include_qr_solution:

        # https://github.com/lincolnloop/python-qrcode

        method = "nothing"  # "basic" #

        if method == "basic":
            # Simple factory, just a set of rects.
            factory = qrcode.image.svg.SvgImage
        elif method == "fragment":
            # Fragment factory (also just a set of rects)
            factory = qrcode.image.svg.SvgFragmentImage
        else:
            # Combined path factory, fixes white space that may occur when zooming
            factory = qrcode.image.svg.SvgPathImage

        qr = qrcode.QRCode(box_size=3, border=0)
        qr.add_data(qr_data)
        qr_img2 = qr.make_image(
            image_factory=factory, fill_color="green", back_color="red"
        )

        s.append(
            draw.Image(
                drawing_size,
                padding,
                qr_size,
                qr_size,
                data=qr_img2.to_string(),
                mime_type="image/svg+xml",
                embed=True,
            )
        )
        s.append(
            draw.Text(
                "Solution",
                fontsize // 3,
                drawing_width - padding,
                qr_size + padding,
                text_anchor="end",
                dominant_baseline="hanging",  # "middle",#
                fill=numbercolor,
            )
        )
    return s


if __name__ == "__main__":
    s = create_svg()
    print(len(s.as_svg()))
    print(s.as_svg())
