from typing import List, Optional
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session

from sqlalchemy import func

from app import schema, models, oauth2
from app.database import get_db

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)


# @router.get("/")
@router.get("/", response_model=List[schema.PostOneOut])
async def posts(db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user),
                limit: int = 10, skip: int = 0, search: Optional[str] = ""):

    # cursor.execute("""SELECT * from posts""")

    # posts = cursor.fetchall()

    print(search)

    posts = db.query(models.Post).filter(
        models.Post.title.contains(search)).limit(limit).offset(skip).all()

    query_results = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
        models.Post.title.contains(search)).limit(limit).offset(skip).all()

    formatted_results = [
        {
            "post": post,
            "votes": votes
        }
        for post, votes in query_results
    ]

    print(formatted_results)
    return formatted_results


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.Post)
async def create_posts(post: schema.PostCreate, db: Session = Depends(get_db),
                       current_user=Depends(oauth2.get_current_user)):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
    #                 (post.title, post.content, post.published))

    # new_post = cursor.fetchone()

    # conn.commit()
    new_post = models.Post(owner_id=current_user.id, **post.dict())

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get("/{id}", response_model=schema.PostOneOut)
def get_post(id: int, response: Response, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):

    # cursor.execute("""SELECT * FROM posts where id = %s""", (str(id)))

    # post = cursor.fetchone()

    # post = db.query(models.Post).filter(models.Post.id == id).first()

    post_result = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

    if not post_result:
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return{"data": f"post with {id} was not found"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with {id} was not found")

    post_data = {
        "post": post_result[0],
        "votes": post_result[1]
    }
    print(post_data)

    return post_data


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):

    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id)))
    # deleted_post = cursor.fetchone()

    # conn.commit()

    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} not found")

    if post.first().owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schema.Post)
def update_post(id: int, post_arg: schema.PostCreate, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):

    # cursor.execute("""UPDATE posts SET title=%s, content=%s, published=%s WHERE id=%s RETURNING *""",(post.title, post.content,
    #                     post.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} not found")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")

    post_query.update(post_arg.dict(), synchronize_session=False)

    db.commit()

    return post_query.first()
