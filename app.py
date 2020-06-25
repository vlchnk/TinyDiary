from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('case.html')


@app.route('/<user>')
def show_user_profile(user):
    # Show posts this user
    return render_template('posts.html', user=user)


@app.route('/<user>/set')
def show_user_profile(user):
    # Show settings panel this user
    return render_template('user.html', user=user)


@app.route('/<user>/<int:post_id>')
def show_post(user,post_id):
    # Show post with this id, id - int number
    return render_template('post.html', post_id=post_id, user=user)


if __name__ == '__main__':
    app.debug = True
    app.run() #host='0.0.0.0'