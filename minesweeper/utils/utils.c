#include <Python.h>

int *surround_coords(int x, int y)
{
    int offsets[8][2] = {{-1, -1},
                         {-1, 0},
                         {-1, 1},
                         {0, -1},
                         {0, 1},
                         {1, -1},
                         {1, 0},
                         {1, 1}};
    int *lst = malloc((2 * 8) * sizeof(int));
    for (int i = 0; i < 8; i++)
    {
        lst[(i * 2) + 0] = x + offsets[i][0];
        lst[(i * 2) + 1] = y + offsets[i][1];
    }
    return lst;
}

int test_bombs(int *bombs, int *board, int *number_tiles, int *guess_tiles,
               int width, int height, int len_guess, int len_number)
{
    for (int i = 0; i < len_number; i++)
    {
        int x = number_tiles[(i * 2) + 0];
        int y = number_tiles[(i * 2) + 1];
        int bomb = 0;
        int unknown = 0;
        int *coords = surround_coords(x, y);
        for (int j = 0; j < 8; j++)
        {
            int coord_x = coords[(j * 2) + 0];
            int coord_y = coords[(j * 2) + 1];
            for (int k = 0; k < len_guess; k++)
            {
                if (coord_x == guess_tiles[(k * 2) + 0] && coord_y == guess_tiles[(k * 2) + 1])
                {
                    if (bombs[k] == 1)
                        bomb++;
                    else if (bombs[k] == -1)
                        unknown++;
                }
            }
            if (coord_x < 0 || coord_y < 0)
                continue;
            if (coord_x >= width || coord_y >= height)
                continue;
            if (board[(coord_y * width) + coord_x] == 11)
                bomb++;
        }
        if (bomb > board[(y * width) + x])
            return 0;
        if ((bomb + unknown) < board[(y * width) + x])
            return 0;
    }
    return 1;
}

int *append(int *lst, int *bombs, int possibilities, int len)
{
    int *result = malloc((len * (possibilities + 1)) * sizeof(int));
    for (size_t i = 0; i < possibilities; i++)
        for (size_t j = 0; j < len; j++)
            result[(i * len) + j] = lst[(i * len) + j];
    for (size_t j = 0; j < len; j++)
        result[((possibilities)*len) + j] = bombs[j];
    return result;
}

int bomb_full(int *bombs, int len)
{
    for (size_t i = 0; i < len; i++)
        if (bombs[i] == -1)
            return 0;
    return 1;
}

double *mean(int *list_bombs, int possibilities, int len)
{
    double *result = malloc(len * sizeof(double));
    for (size_t i = 0; i < len; i++)
    {
        int sum = 0;
        for (size_t j = 0; j < possibilities; j++)
            sum += list_bombs[(j * len) + i];
        result[i] = (double)sum / (double)possibilities;
    }
    return result;
}

double *PossibleBombs(int *board, int *guess_tiles, int *number_tiles,
                      int width, int height, int len_guess, int len_number)
{
    int *lst;
    int *bombs = malloc(len_guess * sizeof(int));
    int *used_bombs = malloc((2 * len_guess) * sizeof(int));
    int possibilities = 0;
    for (int i = 0; i < len_guess; i++)
    {
        bombs[i] = -1;
        for (int j = 0; j < 2; j++)
            used_bombs[(i * 2) + j] = 0;
    }
    int turn = 0;
    while (turn != -1)
    {
        if (turn == len_guess)
        {
            turn--;
            for (int i = 0; i < 2; i++)
                used_bombs[(turn * 2) + i] = 0;
            bombs[turn] = -1;
            turn--;
        }
        else
        {
            // check for unused number
            int number_to_use = -1;
            for (int choice = 0; choice <= 1; choice++)
            {
                if (!used_bombs[(turn * 2) + choice])
                {
                    number_to_use = choice;
                    break;
                }
            }
            // no other unused number
            if (number_to_use < 0)
            {
                for (int i = 0; i < 2; i++)
                    used_bombs[(turn * 2) + i] = 0;
                bombs[turn] = -1;
                turn--; // go back one step
            }
            // test the number
            else
            {
                bombs[turn] = number_to_use;
                used_bombs[(turn * 2) + number_to_use] = 1;
                if (test_bombs(bombs, board, number_tiles, guess_tiles,
                               width, height, len_guess, len_number))
                    turn++;
                else
                    bombs[turn] = -1;
            }
        }
        if (bomb_full(bombs, len_guess) && test_bombs(bombs, board, number_tiles, guess_tiles,
                                                      width, height, len_guess, len_number))
        {
            int *new_lst = append(lst, bombs, possibilities, len_guess);
            lst = new_lst;
            possibilities++;
        }
    }
    printf("possibilities %i\n", possibilities);
    return mean(lst, possibilities, len_guess);
}

static PyObject *_possible_bombs(PyObject *self, PyObject *args)
{
    PyObject *board;
    PyObject *guess_tiles;
    PyObject *number_tiles;

    int width;
    int height;
    int *iboard;
    int *iguess_tiles;
    int *inumber_tiles;
    Py_ssize_t len_guess;
    Py_ssize_t len_number;

    double *result;
    if (!PyArg_ParseTuple(args, "iiOOO", &width, &height, &board, &guess_tiles, &number_tiles))
        return NULL;

    //////////////////// BOARD ////////////////////
    board = PySequence_Fast(board, "argument must be iterable");
    if (!board)
        return 0;
    // make board array
    iboard = malloc((height * width) * sizeof(int));
    if (!iboard)
    {
        Py_DECREF(board);
        return PyErr_NoMemory();
    }
    // place datas in array
    for (int y = 0; y < height; y++)
    {
        PyObject *item = PySequence_Fast_GET_ITEM(board, y);
        if (!item)
        {
            Py_DECREF(board);
            free(iboard);
            return 0;
        }
        for (int x = 0; x < width; x++)
        {
            PyObject *fitem;
            PyObject *value = PySequence_Fast_GET_ITEM(item, x);
            if (!value)
            {
                Py_DECREF(board);
                free(iboard);
                return 0;
            }
            fitem = PyNumber_Long(value);
            if (!fitem)
            {
                Py_DECREF(board);
                free(iboard);
                PyErr_SetString(PyExc_TypeError, "all items must be numbers");
                return 0;
            }
            iboard[y * width + x] = PyLong_AsLong(fitem);
            Py_DECREF(fitem);
        }
    }
    Py_DECREF(board);

    ///////////////// GUESS TILES /////////////////
    guess_tiles = PySequence_Fast(guess_tiles, "argument must be iterable");
    if (!guess_tiles)
        return 0;
    len_guess = PySequence_Fast_GET_SIZE(guess_tiles);
    // make guess_tiles array
    iguess_tiles = malloc((len_guess * 2) * sizeof(int));
    if (!iguess_tiles)
    {
        Py_DECREF(guess_tiles);
        return PyErr_NoMemory();
    }
    // place datas in array
    for (int i = 0; i < len_guess; i++)
    {
        PyObject *item = PySequence_Fast_GET_ITEM(guess_tiles, i);
        if (!item)
        {
            Py_DECREF(guess_tiles);
            free(iguess_tiles);
            return 0;
        }
        for (int j = 0; j < 2; j++)
        {
            PyObject *fitem;
            PyObject *value = PySequence_Fast_GET_ITEM(item, j);
            if (!value)
            {
                Py_DECREF(guess_tiles);
                free(iguess_tiles);
                return 0;
            }
            fitem = PyNumber_Long(value);
            if (!fitem)
            {
                Py_DECREF(guess_tiles);
                free(iguess_tiles);
                PyErr_SetString(PyExc_TypeError, "all items must be numbers");
                return 0;
            }
            iguess_tiles[i * 2 + j] = PyLong_AsLong(fitem);
            Py_DECREF(fitem);
        }
    }
    Py_DECREF(guess_tiles);

    ///////////////// NUMBER TILES ////////////////
    number_tiles = PySequence_Fast(number_tiles, "argument must be iterable");
    if (!number_tiles)
        return 0;
    len_number = PySequence_Fast_GET_SIZE(number_tiles);
    // make number_tiles array
    inumber_tiles = malloc((len_number * 2) * sizeof(int));
    if (!inumber_tiles)
    {
        Py_DECREF(number_tiles);
        return PyErr_NoMemory();
    }
    // place datas in array
    for (int i = 0; i < len_number; i++)
    {
        PyObject *item = PySequence_Fast_GET_ITEM(number_tiles, i);
        if (!item)
        {
            Py_DECREF(number_tiles);
            free(inumber_tiles);
            return 0;
        }
        for (int j = 0; j < 2; j++)
        {
            PyObject *fitem;
            PyObject *value = PySequence_Fast_GET_ITEM(item, j);
            if (!value)
            {
                Py_DECREF(number_tiles);
                free(inumber_tiles);
                return 0;
            }
            fitem = PyNumber_Long(value);
            if (!fitem)
            {
                Py_DECREF(number_tiles);
                free(inumber_tiles);
                PyErr_SetString(PyExc_TypeError, "all items must be numbers");
                return 0;
            }
            inumber_tiles[i * 2 + j] = PyLong_AsLong(fitem);
            Py_DECREF(fitem);
        }
    }
    Py_DECREF(number_tiles);

    /////////////////// RESULT ////////////////////
    result = PossibleBombs(iboard, iguess_tiles, inumber_tiles,
                           width, height, (int)len_guess, (int)len_number);
    free(iboard);
    free(iguess_tiles);
    free(inumber_tiles);

    ///////////////// PYTHON LIST /////////////////
    Py_ssize_t list_length = len_guess;
    PyObject *possible_bombs = PyList_New(list_length);
    for (Py_ssize_t i = 0; i < list_length; i++)
    {
        PyObject *object = PyFloat_FromDouble(result[i]);
        PyList_SetItem(possible_bombs, i, object);
    }
    return Py_BuildValue("O", possible_bombs);
}

static PyObject *version(PyObject *self)
{
    return Py_BuildValue("s", "version 1.0");
}

static PyMethodDef utilsMethods[] = {
    {"_possible_bombs", _possible_bombs, METH_VARARGS, "Calculate color distance"},
    {"version", (PyCFunction)version, METH_NOARGS, "returns the version."},
    {NULL, NULL, 0, NULL}};

static struct PyModuleDef utilsModule = {
    PyModuleDef_HEAD_INIT,
    "utilsModule",
    "Color calculation module.",
    -1,
    utilsMethods};

PyMODINIT_FUNC PyInit_utilsModule(void)
{
    return PyModule_Create(&utilsModule);
}