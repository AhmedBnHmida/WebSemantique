import React, { useEffect, useState } from 'react';
import { blogsAPI } from '../../utils/api';
import './Blogs.css';

const Blogs = () => {
  const [blogs, setBlogs] = useState([]);
  const [keyword, setKeyword] = useState('');
  const [title, setTitle] = useState('');
  const [date, setDate] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadBlogs();
  }, []);

  const loadBlogs = async () => {
    try {
      setLoading(true);
      const res = await blogsAPI.getAll();
      setBlogs(res.data || res);
    } catch (err) {
      console.error('Error loading blogs', err);
    } finally {
      setLoading(false);
    }
  };

  // perform a search with current filters
  const performSearch = async (filters) => {
    try {
      setLoading(true);
      const res = await blogsAPI.search(filters);
      const data = res.data || res;
      setBlogs(data);
    } catch (err) {
      console.error('Search error', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e && e.preventDefault();
    const t = title.trim();
    const k = keyword.trim();
    const d = date; // YYYY-MM-DD from input

    if (!t && !k && !d) {
      loadBlogs();
      return;
    }

    const payload = { title: t, keyword: k };
    if (d) payload.date_from = d; // backend accepts date_from/date_to

    performSearch(payload);
  };

  // Debounce automatic search when filters change
  useEffect(() => {
    const anyFilter = title.trim() || keyword.trim() || date;
    const timer = setTimeout(() => {
      if (anyFilter) {
        handleSearch();
      } else {
        // if no filters, load all
        loadBlogs();
      }
    }, 500); // 500ms debounce

    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [title, keyword, date]);

  return (
    <div className="blogs-page">
      <h2>Blogs</h2>

      <form onSubmit={handleSearch} className="blogs-search-form">
        <input
          placeholder="Search by title..."
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="search-input"
        />
        <input
          placeholder="Search by keywords..."
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          className="search-input"
        />
        <input
          type="date"
          placeholder="Date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="search-input"
        />
        {/* Search button removed — search is automatic on input change */}
        <button 
          type="button" 
          className="clear-button"
            onClick={() => { 
            setKeyword(''); 
            setTitle(''); 
            setDate('');
            loadBlogs(); 
          }}
          disabled={loading}
        >
          Clear
        </button>
      </form>

      <div className="blogs-list">
        {loading ? (
          <div className="loading">Searching blogs...</div>
        ) : blogs && blogs.length ? (
          blogs.map((blog, idx) => {
            const title = blog.blogTitle || blog.title || 'Untitled';
            const content = blog.blogContent || blog.content || '';
            const excerpt = content.length > 220 ? content.slice(0, 220) + '…' : content;
            const date = blog.publicationDate || '';
            const category = blog.category || '';

            // choose a stable seed for the image: prefer shortId, then id, then index
            const seed = blog.shortId || blog.id || `blog-${idx}`;
            const imgSrc = `https://picsum.photos/seed/${encodeURIComponent(seed)}/800/500`;

            return (
              <div key={idx} className="blog-card">
                <div className="blog-card-inner">
                  <div className="blog-image" aria-hidden="true">
                    <img src={imgSrc} alt={title} />
                  </div>
                  <div className="blog-body">
                    <h3>{title}</h3>
                    <div className="blog-meta">
                      <span className="blog-date">{date}</span>
                      {category && (
                        <span className="blog-category category-badge">{category}</span>
                      )}
                    </div>
                    <p className="blog-excerpt">{excerpt}</p>
                    <div className="blog-actions">
                      <button className="read-more">Read more</button>
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        ) : (
          <p className="no-results">No blogs found matching your search.</p>
        )}
      </div>
    </div>
  );
};

export default Blogs;
